/*
 * ________________________________________________________________________________________________________
 * Copyright (c) 2017 InvenSense Inc. All rights reserved.
 *
 * This software, related documentation and any modifications thereto (collectively “Software”) is subject
 * to InvenSense and its licensors' intellectual property rights under U.S. and international copyright
 * and other intellectual property rights laws.
 *
 * InvenSense and its licensors retain all intellectual property and proprietary rights in and to the Software
 * and any use, reproduction, disclosure or distribution of the Software without an express license agreement
 * from InvenSense is strictly prohibited.
 *
 * EXCEPT AS OTHERWISE PROVIDED IN A LICENSE AGREEMENT BETWEEN THE PARTIES, THE SOFTWARE IS
 * PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
 * TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT.
 * EXCEPT AS OTHERWISE PROVIDED IN A LICENSE AGREEMENT BETWEEN THE PARTIES, IN NO EVENT SHALL
 * INVENSENSE BE LIABLE FOR ANY DIRECT, SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, OR ANY
 * DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
 * NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
 * OF THE SOFTWARE.
 * ________________________________________________________________________________________________________
 */

/* InvenSense drivers and utils */
#include "Invn/Devices/Drivers/Iam20680/Iam20680Defs.h"
#include "Invn/Devices/Drivers/Iam20680/Iam20680ExtFunc.h"
#include "Invn/Devices/Drivers/Iam20680/Iam20680Driver_HL.h"
#include "Invn/Devices/Drivers/Iam20680/Iam20680SelfTest.h"
#include "Invn/Devices/Drivers/Iam20680/Iam20680Product.h"

#include "Invn/EmbUtils/Message.h"

#include "example-selftest.h"
#include "system.h"

/* Just a handy variable to handle the iam20680 object */
static inv_iam20680_t icm_device;

/* Offset registers are updated after device reset */
static int isOffsetUpdated = 0;

int SetupInvDevice(int (*read_reg)(void * context, uint8_t reg, uint8_t * buf, uint32_t len),
				   int (*write_reg)(void * context, uint8_t reg, const uint8_t * buf, uint32_t len),
				   inv_bool_t isSPI)
{
	int rc = 0;
	uint8_t who_am_i;

	/* Initialize iam20680 serif structure */
	struct inv_iam20680_serif iam20680_serif;

	iam20680_serif.context   = 0; /* no need */
	iam20680_serif.read_reg  = (*read_reg);
	iam20680_serif.write_reg = (*write_reg);
	iam20680_serif.is_spi    = isSPI;
	if(isSPI) {
		/* Init SPI communication: SPI1 - SCK(PA5) / MISO(PA6) / MOSI(PA7) / CS(PB6) */
		iam20680_serif.max_read  = 1024*32; /* maximum number of bytes allowed per serial read */
		iam20680_serif.max_write = 1024*32; /* maximum number of bytes allowed per serial write */
		INV_MSG(INV_MSG_LEVEL_INFO, "Opening serial interface through SPI");
	}else {
		/* Init I2C communication: I2C1 - SCL(PB8) / SDA(PB9) */
		iam20680_serif.max_read  = 64; /* maximum number of bytes allowed per serial read */
		iam20680_serif.max_write = 64; /* maximum number of bytes allowed per serial write */
		INV_MSG(INV_MSG_LEVEL_INFO, "Opening serial interface through I2C");
	}

	/* Reset iam20680 driver states */
	memset(&icm_device, 0, sizeof(icm_device));
	icm_device.serif = iam20680_serif;

	/* Check WHOAMI */
	rc = inv_iam20680_get_who_am_i(&icm_device, &who_am_i);
	#if (SERIF_TYPE_I2C == 1)
	if((rc != INV_ERROR_SUCCESS) || (who_am_i != EXPECTED_WHOAMI)) {
		if(!isSPI) {
			/* Check i2c bus stuck and clear the bus */
			twi_clear_bus();
		}
	
		/* Retry who_am_i check */
		rc = inv_iam20680_get_who_am_i(&icm_device, &who_am_i);
	}
	#endif

	if(rc != INV_ERROR_SUCCESS)
		return rc;

	if(who_am_i != EXPECTED_WHOAMI) {
		INV_MSG(INV_MSG_LEVEL_ERROR, "Bad WHOAMI value. Got 0x%02x. Expected 0x%02x.", who_am_i, EXPECTED_WHOAMI);
	}

	/* Initialize device */
	rc = inv_iam20680_init(&icm_device);
	
	inv_iam20680_get_trim_offset(&icm_device);
	INV_MSG(INV_MSG_LEVEL_INFO, "ACC Trim offset (g): x=0x%x, y=0x%x, z=0x%x",icm_device.accel_trim_offset[0],icm_device.accel_trim_offset[1],icm_device.accel_trim_offset[2]);

	return rc;
}

void RunSelfTest(void)
{
	int rc = 0;

	rc = inv_iam20680_run_selftest(&icm_device);
	/* Check for GYR success (1 << 0) and ACC success (1 << 1) */
	if ( (rc & 0x1)) {
		INV_MSG(INV_MSG_LEVEL_INFO, "Gyro Selftest PASS");
	} else {
		INV_MSG(INV_MSG_LEVEL_INFO, "Gyro Selftest FAIL");
	}
	if ( (rc & 0x2)) {
		INV_MSG(INV_MSG_LEVEL_INFO, "Accel Selftest PASS");
	} else {
		INV_MSG(INV_MSG_LEVEL_INFO, "Accel Selftest FAIL");
	}
}



void ApplyOffset(int isAccelLpMode,int isGyroLpmode )
{
	inv_iam20680_apply_offset(&icm_device,isAccelLpMode,isGyroLpmode);
	isOffsetUpdated = 1;
}


/*!
 * \brief Display Bias values calculated from factory calib
 */
static void DisplayBias(void)
{
	int raw_accel_bias[6] = {0}; /* [x_ln_bias,y_ln_bias,z_ln_bias,x_lp_bias,y_lp_bias,z_lp_bias] */
	int raw_gyro_bias[6] = {0};
		
	/* Get Low Noise / Low Power bias computed scaled by 2^16 */
	inv_iam20680_get_scaled_bias(&icm_device, raw_gyro_bias, raw_accel_bias);
	
	INV_MSG(INV_MSG_LEVEL_INFO, "GYR LN bias (FS=250dps) (dps): x=%f, y=%f, z=%f",
			(float)(raw_gyro_bias[0] / (float)(1 << 16)), (float)(raw_gyro_bias[1] / (float)(1 << 16)), (float)(raw_gyro_bias[2] / (float)(1 << 16)));
	INV_MSG(INV_MSG_LEVEL_INFO, "GYR LP bias (FS=250dps) (dps): x=%f, y=%f, z=%f",
			(float)(raw_gyro_bias[3] / (float)(1 << 16)), (float)(raw_gyro_bias[4] / (float)(1 << 16)), (float)(raw_gyro_bias[5] / (float)(1 << 16)));
	INV_MSG(INV_MSG_LEVEL_INFO, "ACC LN bias (FS=2g) (g): x=%f, y=%f, z=%f",
			(float)(raw_accel_bias[0] / (float)(1 << 16)), (float)(raw_accel_bias[1] / (float)(1 << 16)), (float)(raw_accel_bias[2] / (float)(1 << 16)));
	INV_MSG(INV_MSG_LEVEL_INFO, "ACC LP bias (FS=2g) (g): x=%f, y=%f, z=%f",
			(float)(raw_accel_bias[3] / (float)(1 << 16)), (float)(raw_accel_bias[4] / (float)(1 << 16)), (float)(raw_accel_bias[5] / (float)(1 << 16)));

}

int RunFactoryCalib(void)
{
	int rc = 0;
	
	if ( isOffsetUpdated )
	{
		/* if offset registers are updated, gyro and accel offset needs to be initialized with trim offset 
		    before factory calibration calculation is performed to ensure offset is measured correctly **/
		inv_iam20680_set_trim_offset(&icm_device);
	}
	INV_MSG(INV_MSG_LEVEL_INFO, "Factory Calib Collecting LN/LP bias");
	rc = inv_iam20680_run_factory_calib(&icm_device);
	if ( rc) {
		INV_MSG(INV_MSG_LEVEL_INFO, "Factory Calib Collecting LN/LP bias FAIL");
		return rc;
	} 
	
	/* Get Low Noise / Low Power bias computed scaled by 2^16 */
	DisplayBias();
	
	/* compute offset and save in struct which can be applied to chip based on mode of sensors */
	inv_iam20680_compute_offset(&icm_device);
	
	return rc;
}