#!/usr/bin/env python3

import argparse
from datetime import datetime
import os
import urllib.request
import json
import numpy as np
import time
import sys
from PIL import Image
from threading import Thread, Lock
import math


class RemoteRegAccess:

    def __init__(self, host, port=80):
        self.host = host
        self.port = port

    def read(self, camera, reg):
        with urllib.request.urlopen(
                f"http://{self.host}:{self.port}/api/v1.0/cppm/cameras/{camera}/register/deserializer/0x{reg:x}") as response:
            resp = response.read()
            resp = json.loads(resp)
            return int(resp["value"], 16)

    def write(self, camera, reg, val):
        urllib.request.urlopen(
            f"http://{self.host}:{self.port}/api/v1.0/cppm/cameras/{camera}/register/deserializer/0x{reg:x}/0x{val:x}")


class MarginAnalysis:
    REG_STS1 = 0x4d
    REG_STS2 = 0x4e
    REG_BCC_STATUS = 0x47
    REG_RX_STS = 0x7a
    REG_CSI_ERR_CNT = 0x7b
    REG_PAR_ERR_CNT_MSB = 0x55
    REG_PAR_ERR_CNT_LSB = 0x56

    # Registers and addresses for indirect registers access
    REG_IND_ACC_CTL = 0xb0
    REG_IND_ACC_ADDR = 0xb1
    REG_IND_ACC_DATA = 0xb2

    ADDR_FPD_CLK_DLY = 0x08
    ADDR_FPD_DAT_DLY = 0x09

    # These register read/writes are per FPD port, as configured by FPD3_PORT_SEL
    REG_FPD3_PORT_SEL = 0x4c
    REG_FPD_ADAPTIVE_EQ_BYPASS = 0xd4

    def __init__(self, des_regs, dwell_time, sp_min, sp_max):
        self.des_regs = des_regs
        self.dwell_time = dwell_time
        self.reg_lock = Lock()
        self.stats = {}
        self.reg_backup = {}
        self.sp_min = sp_min
        self.sp_max = sp_max
        self.stop_monitor = False

    def read_ind_reg(self, camera, addr):
        port = camera % 4
        retval = None

        with self.reg_lock:
            self.des_regs.write(camera, self.REG_IND_ACC_CTL, (port + 1) << 2)
            self.des_regs.write(camera, self.REG_IND_ACC_ADDR, addr)
            retval = self.des_regs.read(camera, self.REG_IND_ACC_DATA)

        return retval

    def write_ind_reg(self, camera, addr, val):
        port = camera % 4

        with self.reg_lock:
            self.des_regs.write(camera, self.REG_IND_ACC_CTL, (port + 1) << 2)
            self.des_regs.write(camera, self.REG_IND_ACC_ADDR, addr)
            self.des_regs.write(camera, self.REG_IND_ACC_DATA, val)

    def set_strobe_alt(self, camera, val):
        self.des_regs.write(camera, 0x41, (val << 4) | val)

    def set_strobe(self, camera, val):

        # Extra delay off
        dd_reg_val = 0x8
        cd_reg_val = 0x8

        if val < 6:
            cd_reg_val = (7 - val)
        elif val < 13:
            cd_reg_val = (13 - val) | 0x8
        elif val < 21:
            dd_reg_val = (val - 13) | 0x8
        else:
            dd_reg_val = (val - 19)

        self.write_ind_reg(camera, self.ADDR_FPD_CLK_DLY, cd_reg_val)
        self.write_ind_reg(camera, self.ADDR_FPD_DAT_DLY, dd_reg_val)

    def get_strobe(self, camera):
        cd_reg_val = self.read_ind_reg(camera, self.ADDR_FPD_CLK_DLY)
        dd_reg_val = self.read_ind_reg(camera, self.ADDR_FPD_DAT_DLY)

        return (cd_reg_val, dd_reg_val)

    def read_fpd_reg(self, camera, addr):
        port = camera % 4
        retval = None

        with self.reg_lock:
            self.des_regs.write(camera, self.REG_FPD3_PORT_SEL, port << 4)
            retval = self.des_regs.read(camera, addr)

        return retval

    def write_fpd_reg(self, camera, addr, val):
        port = camera % 4

        with self.reg_lock:
            self.des_regs.write(camera, self.REG_FPD3_PORT_SEL, 0x1 << port)
            self.des_regs.write(camera, addr, val)

    def set_eq(self, camera, val):
        if val <= 0x7:
            reg_val = (val << 5) | 1
        else:
            reg_val = (7 << 5) | ((val - 7) << 1) | 1

        self.des_regs.write(camera, self.REG_FPD_ADAPTIVE_EQ_BYPASS, reg_val)

    def get_eq(self, camera):
        regval = self.read_fpd_reg(camera, self.REG_FPD_ADAPTIVE_EQ_BYPASS)
        aeq_enabled = (regval & 0x1) == 0
        eq_stage1 = (regval >> 5) & 0x7
        eq_stage2 = (regval >> 1) & 0x7

        return (eq_stage1 | (eq_stage2 << 3), aeq_enabled)

    def initial_setup(self, camera):
        self.des_regs.write(camera, 0x40, 0x0)  # Nobody knows what this does
        self.des_regs.write(camera, 0x42, 0x0)  # Disable sfilter
        self.des_regs.write(camera, 0xd2, 0x0)  # Disable AEQ

    def backup(self, cameras):
        for des in set([cam / 4 for cam in cameras]):
            for reg in (0x40, 0x42, 0xd2):
                self.reg_backup[(des * 4, reg)] = self.des_regs.read(des * 4, reg)

    def restore(self, cameras):
        for (camera, reg), val in self.reg_backup.items():
            self.des_regs.write(camera, reg, val)

        for camera in cameras:
            port = camera % 4

            # Restore strobe setting
            self.des_regs.write(camera, self.REG_IND_ACC_CTL, (port + 1) << 2)
            self.des_regs.write(camera, self.REG_IND_ACC_ADDR, 0x08)
            self.des_regs.write(camera, self.REG_IND_ACC_DATA, 0x00)

        # Restart AEQ
        for (camera, reg), val in self.reg_backup.items():
            if reg == 0xd2:
                self.des_regs.write(camera, 0xd2, val | 0x4)

    def iterate(self, camera, sp_min, sp_max):
        for sp in range(sp_min, sp_max + 1):
            self.set_strobe(camera, sp)

            for eq in range(0, 15):
                self.set_eq(camera, eq)

                yield (sp - sp_min, eq)

    def iterate_alt(self, camera, sp_min, sp_max):
        for sp in range(sp_min, sp_max + 1):
            self.set_strobe_alt(camera, sp)

            for eq in range(0, 15):
                self.set_eq(camera, eq)

                # Restart AEQ
                self.des_regs.write(camera, 0xd2, 0x9c)

                yield (sp - sp_min, eq)

    def margin_analysis(self, camera, use_alt, log=None):

        if self.sp_min is None:
            sp_min = 0
        else:
            if use_alt:
                sp_min = max(0, min(14, self.sp_min + 7))
            else:
                sp_min = max(0, min(26, self.sp_min + 13))

        if self.sp_max is None:
            if use_alt:
                sp_max = 14
            else:
                sp_max = 26
        else:
            if use_alt:
                sp_max = max(0, min(14, self.sp_max + 7))
            else:
                sp_max = max(0, min(26, self.sp_max + 13))

        port = camera % 4

        sp_width = sp_max - sp_min + 1
        result = np.full((15, sp_width), -1, dtype=np.int)
        if use_alt:
            it = self.iterate_alt
            # Set base delay to 0
            self.set_strobe(camera, 13)
        else:
            self.initial_setup(camera)
            it = self.iterate

        for sp, eq in it(camera, sp_min, sp_max):
            self.stats[camera] = [sp, eq, 0]

            # Give it a chance to lock
            time.sleep(0.01)

            sts1 = self.des_regs.read(camera, self.REG_STS1)

            if (sts1 & 0x3) != 0x3:
                result[eq, sp] = -1
                if log:
                    print(f"{sp:02d}/{eq:02d}:   0x{sts1 & 0xf:x}", file=log, flush=True)
                continue

            # Clear all status registers
            self.des_regs.read(camera, self.REG_RX_STS)
            self.des_regs.read(camera, self.REG_CSI_ERR_CNT)
            self.des_regs.read(camera, self.REG_PAR_ERR_CNT_MSB)
            self.des_regs.read(camera, self.REG_PAR_ERR_CNT_LSB)
            self.des_regs.read(camera, self.REG_BCC_STATUS)
            self.des_regs.read(camera, self.REG_STS1)
            self.des_regs.read(camera, self.REG_STS2)

            # If DWELL_TIME is more than 1 seconds, check once per second and
            # exit when an error is detected. This speeds the scan up since we
            # don't have to wait the maximum time for all settings.
            if self.dwell_time > 1:
                n = int(self.dwell_time)
                t = 1
            else:
                n = 1
                t = self.dwell_time

            for i in range(n):
                self.stats[camera] = [sp, eq, i]
                time.sleep(t)

                # Check all the status registers
                sts1 = self.des_regs.read(camera, self.REG_STS1)
                sts2 = self.des_regs.read(camera, self.REG_STS2)
                bcc_status = self.des_regs.read(camera, self.REG_BCC_STATUS)
                rx_sts = self.des_regs.read(camera, self.REG_RX_STS)
                csi_err_cnt = self.des_regs.read(camera, self.REG_CSI_ERR_CNT)
                par_err_cnt = self.des_regs.read(camera, self.REG_PAR_ERR_CNT_LSB)
                par_err_cnt |= (self.des_regs.read(camera, self.REG_PAR_ERR_CNT_MSB) << 8)

                if (sts1 & 0x3f) == 0x3 and (sts2 & 0xae) == 0x04 and \
                        rx_sts == 0x00 and csi_err_cnt == 0 and par_err_cnt == 0:
                    result[eq, sp] = 0
                else:
                    # Store how long it took until error
                    result[eq, sp] = (i + 1)
                    break

            if log:
                print(
                    f"{sp:02d}/{eq:02d}/{i}: 0x{sts1 & 0xf:x}\t0x{sts2 & 0xbe:x}\t0x{rx_sts:x}\t{par_err_cnt}\t{csi_err_cnt}\t0x{bcc_status:x}",
                    file=log, flush=True)

        if log:
            print(result, file=log, flush=True)

        return result


COLOR_BORDER = (0, 0, 250)


def save_image(filename, ma, center):
    data = np.full((ma.shape[0] * 16 + 3, ma.shape[1] * 16 + 3, 3), 255, dtype=np.uint8)

    for eq in range(ma.shape[0]):
        for sp in range(ma.shape[1]):
            if ma[eq, sp] == 0:
                if (eq, sp) == center:
                    c = (0, 255, 0)
                else:
                    c = (0, 200, 0)
            elif ma[eq, sp] == -1:
                c = (200, 0, 0)
            elif ma[eq, sp] <= 60:
                c = (255, 160, 0)
            else:
                c = (255, 220, 0)

            for x in range(1, 14):
                for y in range(1, 14):
                    data[eq * 16 + x + 2, sp * 16 + y + 2] = c

    b = box(ma, center)
    if b is not None:
        for eq in range(b[0][0] * 16, b[1][0] * 16 + 19):
            for sp in (
            b[0][1] * 16, b[0][1] * 16 + 1, b[0][1] * 16 + 2, b[1][1] * 16 + 16, b[1][1] * 16 + 17, b[1][1] * 16 + 18):
                data[eq, sp] = COLOR_BORDER
        for sp in range(b[0][1] * 16, b[1][1] * 16 + 19):
            for eq in (
            b[0][0] * 16, b[0][0] * 16 + 1, b[0][0] * 16 + 2, b[1][0] * 16 + 16, b[1][0] * 16 + 17, b[1][0] * 16 + 18):
                data[eq, sp] = COLOR_BORDER

    img = Image.fromarray(data, "RGB")
    img.save(filename)


def process_camera(output_dir, ma, camera, use_alt):
    with open(os.path.join(output_dir, f"ma_{camera}.log"), "w") as log:
        result = ma.margin_analysis(camera, use_alt, log)

        try:
            best = best_setting(result)
        except ZeroDivisionError as err:
            best = None

        if best is None:
            print("No solution found for best setting!", file=log)
        else:
            print('Best setting:', best, file=log)

    save_image(os.path.join(output_dir, f"ma_{camera}.png"), result, best)
    np.save(os.path.join(output_dir, f"ma_{camera}.npy"), result)


def monitor(ma):
    while not ma.stop_monitor:
        l = ""
        for cam, s in ma.stats.items():
            l += "{:d}/{:02d}/{:02d}/{:04d}\t".format(cam, *s)
        print(l, end="\r", flush=True)
        time.sleep(0.01)


def centroid(data):
    sum_eq = 0
    sum_sp = 0
    num = 0
    for eq in range(data.shape[0]):
        for sp in range(data.shape[1]):
            if data[eq, sp] == 0:
                sum_eq += eq * 10
                sum_sp += sp * 10
                num += 10
            elif data[eq, sp] != -1:
                # Use regions with lock but errors as tie braker if the good
                # region is perfectly symmetric
                sum_eq += eq
                sum_sp += sp
                num += 1

    if not num:
        return None

    return (int(math.floor(sum_eq / num)), int(round(sum_sp / num)))


def best_setting(data):
    best_width = (0, 0)
    best_eq = -1
    best_sp = -1

    # Skip first and last eq setting, we want at least one row margin
    for eq in range(1, data.shape[0] - 1):
        valid_width = 0
        lock_width = 0
        num_sp = 0
        sum_sp = 0
        for sp in range(data.shape[1]):
            if data[eq - 1, sp] == 0 and \
                    data[eq, sp] == 0 and \
                    data[eq + 1, sp] == 0:
                lock_width += 1
                valid_width += 1
                sum_sp += sp * 10
                num_sp += 10
            elif data[eq, sp] != -1:
                # Use the with of the row itself as a tie breaker
                lock_width += 1
                sum_sp += sp
                num_sp += 1

        if valid_width > best_width[0] or \
                (valid_width == best_width[0] and lock_width > best_width[1]):
            best_width = (valid_width, lock_width)
            best_eq = eq
            best_sp = int(round(sum_sp / num_sp))

    if best_eq == -1:
        return None

    return (best_eq, best_sp)


def box(data, center):
    if center is None:
        return None

    min_sp = data.shape[1]
    max_sp = 0

    eq = center[0]

    for sp in range(data.shape[1]):
        if data[eq, sp] == 0 and \
                data[eq - 1, sp] == 0 and \
                data[eq + 1, sp] == 0:
            min_sp = min(min_sp, sp)
            max_sp = max(max_sp, sp)

    min_eq = data.shape[1]
    max_eq = 0

    for eq in range(center[0], data.shape[0]):
        all_valid = True
        for sp in range(min_sp, max_sp + 1):
            if data[eq, sp] != 0:
                all_valid = False
                break
        if not all_valid:
            break
        max_eq = eq

    for eq in range(center[0], -1, -1):
        all_valid = True
        for sp in range(min_sp, max_sp + 1):
            if data[eq, sp] != 0:
                all_valid = False
                break
        if not all_valid:
            break
        min_eq = eq

    return ((min_eq, min_sp), (max_eq, max_sp))


def run_sp_eq_commands(args, ma):
    ran_command = False

    if args.get_sp_eq:
        ran_command = True
        for cam in args.cameras:
            cd, dd = ma.get_strobe(cam)
            eq, aeq_en = ma.get_eq(cam)
            print(f"Camera {cam} SP-CD:0x{cd:x} SP-DD:0x{dd:x} EQ:{eq} AEQ-EN:{aeq_en}")

    if args.set_strobe != -1:
        ran_command = True
        sp = args.set_strobe
        for cam in args.cameras:
            print(f"Setting Camera {cam} SP:{sp}")
            ma.set_strobe(cam, sp)

    if args.set_eq != -1:
        ran_command = True
        eq = args.set_eq
        for cam in args.cameras:
            print(f"Setting Camera {cam} EQ:{eq}")
            ma.set_eq(cam, eq)

    return ran_command


def run_margin_analysis(args, ma):
    cameras = args.cameras
    use_alt = args.alt
    output_dir = args.output_dir
    threads = []

    print("Before scanning run `sv stop cppm-camera-diag-server` on the CPPM")
    print("Scannning...")

    if not output_dir:
        output_dir = "ma_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    os.mkdir(output_dir)

    monitor_thread = Thread(target=monitor, args=(ma,))
    monitor_thread.start()

    ma.backup(cameras)

    if use_alt:
        for cam in cameras:
            target = process_camera(output_dir, ma, cam, True)
    else:
        for cam in cameras:
            t = Thread(target=process_camera, args=(output_dir, ma, cam, False))
            t.start()
            threads.append(t)

    for t in threads:
        t.join()

    ma.stop_monitor = True
    monitor_thread.join()

    ma.restore(cameras)
    print(f"\nDone. Results stored in \"{output_dir}\"")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="FPD-link margin analysis")

    parser.add_argument("cameras", type=int, nargs="+",
                        help="List of camera ports to scan")

    # Arguments specifying CPPM communication
    parser.add_argument("--host", help="Board IP address", default="10.5.1.71")
    parser.add_argument("--port", type=int, help="Webserver port", default=80)

    # Non-MAP Arguments
    parser.add_argument("--get-sp-eq", help="Only read and report current SP / EQ from specified cameras",
                        default=False, action='store_true')
    parser.add_argument("--set-strobe", help="Set Strobe Position of specified cameras in range [0,27]", type=int,
                        default=-1)
    parser.add_argument("--set-eq",
                        help="Set Equalization of specified cameras in range [0,15]. This will disable AEQ.", type=int,
                        default=-1)

    # Arguments for Margin Analysis Program
    parser.add_argument("--dwell-time", type=float, help="In seconds", default=1.0)
    parser.add_argument("--alt", help="Use alternative test sequence", default=False, action='store_true')
    parser.add_argument("--output-dir", help="Directory where the results are stored")
    parser.add_argument("--min-sp", help="Minimum strobe setting", type=int)
    parser.add_argument("--max-sp", help="Maximum strobe setting", type=int)

    args = parser.parse_args()

    des_regs = RemoteRegAccess(args.host, args.port)

    ma = MarginAnalysis(des_regs, args.dwell_time, args.min_sp, args.max_sp)

    ran_sp_eq_command = run_sp_eq_commands(args, ma)

    # Only do Margin Analysis if no get / set EQ args are provided
    if not ran_sp_eq_command:
        run_margin_analysis(args, ma)
