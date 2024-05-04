/*
 * ________________________________________________________________________________________________________
 * Copyright (c) 2015-2015 InvenSense Inc. All rights reserved.
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

#include "Iam20680SelfTest.h"
#include "Iam20680Defs.h"
#include "Iam20680ExtFunc.h"
#include "Iam20680Transport.h"
#include "Iam20680Driver_HL.h"

#define DEF_ST_SCALE                           	32768
#define DEF_ST_GYRO_FS_DPS                      250
#define DEF_SELFTEST_GYRO_SENS                  (DEF_ST_SCALE / DEF_ST_GYRO_FS_DPS)
#define DEF_ST_PRECISION						1000
#define DEF_ST_ACCEL_FS_MG						2000 /* Accel Full Scale milli G */
#define DEF_ST_TRY_TIMES						2
#define DEF_ST_SAMPLES							200
#define DEF_GYRO_CT_SHIFT_DELTA					500
#define DEF_ACCEL_ST_SHIFT_DELTA				500
#define ACCEL_ST_AL_MIN ((DEF_ACCEL_ST_AL_MIN * DEF_ST_SCALE \
				 / DEF_ST_ACCEL_FS_MG) * DEF_ST_PRECISION)
#define ACCEL_ST_AL_MAX ((DEF_ACCEL_ST_AL_MAX * DEF_ST_SCALE \
				 / DEF_ST_ACCEL_FS_MG) * DEF_ST_PRECISION)
#define DEF_ST_ACCEL_LPF						2
#define DEF_ST_GYRO_LPF							2
#define DEF_SELFTEST_SAMPLE_RATE				0 			/*	1000Hz 	*/
#define DEF_SELFTEST_SAMPLE_RATE_LP				4 			/* 	200Hz 	*/
#define DEF_SELFTEST_SAMPLE_RATE_LP_ACCEL       10			/* 	250Hz	*/
#define DEF_SELFTEST_ACCEL_FS					(0 << 3) 	/* 	2g 		*/
#define DEF_SELFTEST_GYRO_FS					(0 << 3) 	/* 	250dps 	*/
#define DEF_ST_STABLE_TIME						20
#define DEF_GYRO_WAIT_TIME						5
#define DEF_GYRO_WAIT_TIME_LP					50
#define GYRO_ENGINE_UP_TIME                     50

/* Gyro Offset Max Value (dps) */
#define DEF_GYRO_OFFSET_MAX						20
/* Gyro Self Test Absolute Limits ST_AL (dps) */
#define DEF_GYRO_ST_AL							60
/* Accel Self Test Absolute Limits ST_AL (mg) */
#define DEF_ACCEL_ST_AL_MIN						225
#define DEF_ACCEL_ST_AL_MAX						675

#define BYTES_PER_SENSOR                       	6
#define BYTES_PER_TEMP_SENSOR                  	2
#define FIFO_COUNT_BYTE                        	2
#define THREE_AXES                             	3

enum {
	ST_NORMAL_MODE = 0,
	ST_GYRO_LP_MODE = 1,
	ST_ACCEL_LP_MODE = 2
};

/** @brief the registers to recover after self-test
 */
struct recover_regs {
	uint8_t int_enable;		/* REG_INT_ENABLE      */
	uint8_t fifo_en;		/* REG_FIFO_EN         */
	uint8_t user_ctrl;		/* REG_USER_CTRL       */
	uint8_t config;			/* REG_CONFIG          */
	uint8_t gyro_config;	/* REG_GYRO_CONFIG     */
	uint8_t accel_config;	/* REG_ACCEL_CONFIG    */
	uint8_t accel_config_2;	/* REG_ACCEL_CONFIG_2  */
	uint8_t smplrt_div;		/* REG_SAMPLE_RATE_DIV */
	uint8_t lp_mode;		/* REG_LP_MODE_CTRL    */
	uint8_t pwr_mgmt_1;		/* REG_PWR_MGMT_1      */
	uint8_t pwr_mgmt_2;		/* REG_PWR_MGMT_2      */
};

/* Array of ST_FV ( factory Self-Test value) calculated for all values of ST_Code ranging from 1 to 256.
   ST_FV is calculated from ST_Code based on following equation.
   sSelfTestEquation[ST_Code -1] = ( 2620 / pow(2,FS)) * pow ( 1.01,(ST_Code -1 )) 
 **/   
static const uint16_t sSelfTestEquation[256] = {
	2620, 2646, 2672, 2699, 2726, 2753, 2781, 2808,
	2837, 2865, 2894, 2923, 2952, 2981, 3011, 3041,
	3072, 3102, 3133, 3165, 3196, 3228, 3261, 3293,
	3326, 3359, 3393, 3427, 3461, 3496, 3531, 3566,
	3602, 3638, 3674, 3711, 3748, 3786, 3823, 3862,
	3900, 3939, 3979, 4019, 4059, 4099, 4140, 4182,
	4224, 4266, 4308, 4352, 4395, 4439, 4483, 4528,
	4574, 4619, 4665, 4712, 4759, 4807, 4855, 4903,
	4953, 5002, 5052, 5103, 5154, 5205, 5257, 5310,
	5363, 5417, 5471, 5525, 5581, 5636, 5693, 5750,
	5807, 5865, 5924, 5983, 6043, 6104, 6165, 6226,
	6289, 6351, 6415, 6479, 6544, 6609, 6675, 6742,
	6810, 6878, 6946, 7016, 7086, 7157, 7229, 7301,
	7374, 7448, 7522, 7597, 7673, 7750, 7828, 7906,
	7985, 8065, 8145, 8227, 8309, 8392, 8476, 8561,
	8647, 8733, 8820, 8909, 8998, 9088, 9178, 9270,
	9363, 9457, 9551, 9647, 9743, 9841, 9939, 10038,
	10139, 10240, 10343, 10446, 10550, 10656, 10763, 10870,
	10979, 11089, 11200, 11312, 11425, 11539, 11654, 11771,
	11889, 12008, 12128, 12249, 12371, 12495, 12620, 12746,
	12874, 13002, 13132, 13264, 13396, 13530, 13666, 13802,
	13940, 14080, 14221, 14363, 14506, 14652, 14798, 14946,
	15096, 15247, 15399, 15553, 15709, 15866, 16024, 16184,
	16346, 16510, 16675, 16842, 17010, 17180, 17352, 17526,
	17701, 17878, 18057, 18237, 18420, 18604, 18790, 18978,
	19167, 19359, 19553, 19748, 19946, 20145, 20347, 20550,
	20756, 20963, 21173, 21385, 21598, 21814, 22033, 22253,
	22475, 22700, 22927, 23156, 23388, 23622, 23858, 24097,
	24338, 24581, 24827, 25075, 25326, 25579, 25835, 26093,
	26354, 26618, 26884, 27153, 27424, 27699, 27976, 28255,
	28538, 28823, 29112, 29403, 29697, 29994, 30294, 30597,
	30903, 31212, 31524, 31839, 32157, 32479, 32804
};

static int save_settings(struct inv_iam20680 * s, struct recover_regs * saved_regs)
{
	int result = 0;
	uint8_t data;

	result |= inv_iam20680_read_reg(s, MPUREG_PWR_MGMT_1, 1, &saved_regs->pwr_mgmt_1);

	/* wake up */
	data = CLK_SEL;
	result |= inv_iam20680_write_reg(s, MPUREG_PWR_MGMT_1, 1, &data);

	result |= inv_iam20680_read_reg(s, MPUREG_INT_ENABLE, 1, &saved_regs->int_enable);
	result |= inv_iam20680_read_reg(s, MPUREG_FIFO_EN, 1, &saved_regs->fifo_en);
	result |= inv_iam20680_read_reg(s, MPUREG_USER_CTRL, 1, &saved_regs->user_ctrl);
	result |= inv_iam20680_read_reg(s, MPUREG_CONFIG, 1, &saved_regs->config);
	result |= inv_iam20680_read_reg(s, MPUREG_GYRO_CONFIG, 1, &saved_regs->gyro_config);
	result |= inv_iam20680_read_reg(s, MPUREG_ACCEL_CONFIG, 1, &saved_regs->accel_config);
	result |= inv_iam20680_read_reg(s, MPUREG_ACCEL_CONFIG_2, 1, &saved_regs->accel_config_2);
	result |= inv_iam20680_read_reg(s, MPUREG_SMPLRT_DIV, 1, &saved_regs->smplrt_div);
	result |= inv_iam20680_read_reg(s, MPUREG_LP_MODE_CFG, 1, &saved_regs->lp_mode);
	result |= inv_iam20680_read_reg(s, MPUREG_PWR_MGMT_2, 1, &saved_regs->pwr_mgmt_2);

	return result;
}

static int recover_settings(struct inv_iam20680 * s, const struct recover_regs * saved_regs)
{
	int result = 0;
	uint8_t data;

	// Stop sensors
	data = BIT_PWR_ALL_OFF_MASK;
	result |= inv_iam20680_write_reg(s, MPUREG_PWR_MGMT_2, 1, &data);

	// Restore sensor configurations
	result |= inv_iam20680_write_reg(s, MPUREG_INT_ENABLE, 1, &saved_regs->int_enable);
	result |= inv_iam20680_write_reg(s, MPUREG_FIFO_EN, 1, &saved_regs->fifo_en);
	result |= inv_iam20680_write_reg(s, MPUREG_USER_CTRL, 1, &saved_regs->user_ctrl);
	result |= inv_iam20680_write_reg(s, MPUREG_CONFIG, 1, &saved_regs->config);
	result |= inv_iam20680_write_reg(s, MPUREG_GYRO_CONFIG, 1, &saved_regs->gyro_config);
	result |= inv_iam20680_write_reg(s, MPUREG_ACCEL_CONFIG, 1, &saved_regs->accel_config);
	result |= inv_iam20680_write_reg(s, MPUREG_ACCEL_CONFIG_2, 1, &saved_regs->accel_config_2);
	result |= inv_iam20680_write_reg(s, MPUREG_SMPLRT_DIV, 1, &saved_regs->smplrt_div);
	result |= inv_iam20680_write_reg(s, MPUREG_LP_MODE_CFG, 1, &saved_regs->lp_mode);
	result |= inv_iam20680_write_reg(s, MPUREG_PWR_MGMT_1, 1, &saved_regs->pwr_mgmt_1);
	result |= inv_iam20680_write_reg(s, MPUREG_PWR_MGMT_2, 1, &saved_regs->pwr_mgmt_2);

	return result;
}

/**
*  @brief check gyro self test
*  @param[in] s Pointer to the driver context structure inv_iam20680
*  @param[in] meanNormalTestValues pointer to average value of regular tests.( GX_OS, GY_OS, GZ_OS)
*  @param[in] meanSelfTestValues   pointer to average value of self tests. ( GX_ST_OS, GY_ST_OS, GZ_ST_OS)
*  @return zero as success. A non-zero return value indicates failure in self test.
*/
static int check_gyro_self_test(struct inv_iam20680 * s, int *meanNormalTestValues, int *meanSelfTestValues)
{
	int ret_val = 0;

	uint8_t st_code[3];
	int is_st_fv_value_zero = 0;
	int gyro_st_fv[3] ;  //factory self-test values
	int gyro_st[3]; // gyro self test responses 
	int  st_shift_ratio[3],i;
	int result;

    /* Read ST_Code for all axis */
	result = inv_iam20680_read_reg(s, MPUREG_SELF_TEST_X_GYRO, 3, st_code);
	if (result)
		return result;

	/* For each axis ST_Code get corresponding ST_FV from array */
	for (i = 0; i < 3; i++) {
		if (st_code[i] != 0) {
			gyro_st_fv[i] = sSelfTestEquation[st_code[i] - 1];
		} else {
			gyro_st_fv[i] = 0;
			is_st_fv_value_zero = 1;
		}
	}

	for (i = 0; i < 3; i++) {
		/* calculating gyro self-test responses ( _ST_OS - _OS ) and Upscaling to avoid floating point arithmetic */
		gyro_st[i] = (meanSelfTestValues[i] - meanNormalTestValues[i] ) * DEF_ST_PRECISION;
		if (!is_st_fv_value_zero) {
			/* Self Test Pass/Fail Criteria A */
			st_shift_ratio[i] = (int)(gyro_st[i] / gyro_st_fv[i] );
			if (st_shift_ratio[i] < DEF_GYRO_CT_SHIFT_DELTA )
				ret_val = 1;
		} else {
			/* Self Test Pass/Fail Criteria B */
			if (INV_ABS(gyro_st[i]) < DEF_GYRO_ST_AL * DEF_SELFTEST_GYRO_SENS * DEF_ST_PRECISION)
				ret_val = 1;
		}
	}

	if (ret_val == 0) {
		/* Self Test Pass/Fail Criteria C */
		for (i = 0; i < 3; i++) {
			if (INV_ABS(meanNormalTestValues[i]) > DEF_GYRO_OFFSET_MAX * DEF_SELFTEST_GYRO_SENS * DEF_ST_PRECISION)
				ret_val = 1;
		}
	}

	return ret_val;
}

/**
*  @brief check accel self test
*  @param[in] s Pointer to the driver context structure inv_iam20680
*  @param[in] meanNormalTestValues pointer to average value of regular tests ( AX_OS, AY_OS, AZ_OS)
*  @param[in] meanSelfTestValues   pointer to average value of self tests. ( AX_ST_OS, AY_ST_OS, AZ_ST_OS)
*  @return zero as success. A non-zero return value indicates failure in self test.
*/
static int check_accel_self_test(struct inv_iam20680 * s, int *meanNormalTestValues, int *meanSelfTestValues)
{
	int ret_val = 0;

	uint8_t st_code[3];
	int is_st_fv_value_zero = 0;
	int accel_st_fv[3] ;  //factory self-test values
	int accel_st[3]; // accel self test responses 
	int st_shift_ratio[3], i;
	int result;

    /* Read ST_Code for all axis */
	result = inv_iam20680_read_reg(s, MPUREG_SELF_TEST_X_ACCEL, 3, st_code);
	if (result)
		return result;

    /* For each axis ST_Code get corresponding ST_FV from array */
	for (i = 0; i < 3; i++) {
		if (st_code[i] != 0) {
			accel_st_fv[i] = sSelfTestEquation[st_code[i] - 1];
		} else {
			accel_st_fv[i] = 0;
			is_st_fv_value_zero = 1;
		}
	}
	
	for (i = 0; i < 3; i++) {
		/* calculating accel self-test responses ( _ST_OS - _OS ) and Upscaling to avoid floating point arithmetic */
		accel_st[i] = (meanSelfTestValues[i] - meanNormalTestValues[i])* DEF_ST_PRECISION;
		if (!is_st_fv_value_zero) {
     		/* Self Test Pass/Fail Criteria A */
			st_shift_ratio[i] = (int)(accel_st[i] / accel_st_fv[i] );
			if ((st_shift_ratio[i] < DEF_ACCEL_ST_SHIFT_DELTA ) || (st_shift_ratio[i] >  (DEF_ST_PRECISION + DEF_ACCEL_ST_SHIFT_DELTA) ) )
				ret_val = 1;
		} else {
         	/* Self Test Pass/Fail Criteria B ( factory self-test values ST_OTP is 0) */
			if ((INV_ABS(accel_st[i]) < ACCEL_ST_AL_MIN) || (INV_ABS(accel_st[i]) > ACCEL_ST_AL_MAX) )
				ret_val = 1;
		}
	}

	return ret_val;
}

/*
*  do_test() - collect gyro and accel bias in specified mode and compute avg bias .
*/
static int do_test(struct inv_iam20680 * s, int self_test_flag, int *gyro_result, int *accel_result, int lp_mode)
{
	int result = 0;
	unsigned int fifo_reads_per_second;			// Will contain the approximate number of FIFO reads per second
	unsigned int number_times_fifo_empty = 0;	// Track how many times in a row the FIFO has been empty.

	int i, j, packet_size;
	uint8_t data[BYTES_PER_SENSOR * 2 + BYTES_PER_TEMP_SENSOR], d, dd, da, tmp;
	int fifo_count, packet_count, ind, ss;
	
	if (lp_mode) 
		fifo_reads_per_second = (1000 / DEF_GYRO_WAIT_TIME_LP) + 1;			// The number of FIFO reads per second is ~(1000 ms / gyro wait time). Add 1 to round up.
	else
		fifo_reads_per_second = (1000 / DEF_GYRO_WAIT_TIME) + 1;			// The number of FIFO reads per second is ~(1000 ms / gyro wait time). Add 1 to round up.
	

	/* switch engine */
	d = 0;
	if (lp_mode == ST_GYRO_LP_MODE)
		d = BIT_PWR_ACCEL_STBY_MASK | BIT_PWR_MGMT_2_FIFO_LP_EN_MASK;
	else if (lp_mode == ST_ACCEL_LP_MODE)
		d = BIT_PWR_GYRO_STBY_MASK | BIT_PWR_MGMT_2_FIFO_LP_EN_MASK;

	result |= inv_iam20680_write_reg(s, MPUREG_PWR_MGMT_2, 1, &d);
	inv_iam20680_sleep_us(GYRO_ENGINE_UP_TIME*1000);

	packet_size = BYTES_PER_SENSOR * 2;

	/* clear signal path */
	d = 1;
	result |= inv_iam20680_write_reg(s, MPUREG_USER_CTRL, 1, &d);

	inv_iam20680_sleep_us(30000);

	/* disable interrupt */
	d = 0;
	result |= inv_iam20680_write_reg(s, MPUREG_INT_ENABLE, 1, &d);

	/* disable the sensor output to FIFO */
	d = 0;
	result |= inv_iam20680_write_reg(s, MPUREG_FIFO_EN, 1, &d);

	/* disable fifo reading */
	d = 0;
	result |= inv_iam20680_write_reg(s, MPUREG_USER_CTRL, 1, &d);

	/* setup parameters */
	d = DEF_ST_GYRO_LPF;
	result |= inv_iam20680_write_reg(s, MPUREG_CONFIG, 1, &d);

	/* gyro lp mode */
	if (lp_mode == ST_GYRO_LP_MODE)
		d  = BIT_GYRO_CYCLE_MASK;
	else
		d = 0;
 	result |= inv_iam20680_write_reg(s, MPUREG_LP_MODE_CFG, 1, &d);

	/* set sampling rate */
	if (lp_mode == ST_ACCEL_LP_MODE) {
		/* Set the rate to 250 Hz */
		inv_iam20680_sleep_us(30000);
		result |= inv_iam20680_read_reg(s, MPUREG_LP_MODE_CFG, 1, &d);
		if (lp_mode == ST_ACCEL_LP_MODE)
			d |= DEF_SELFTEST_SAMPLE_RATE_LP_ACCEL;
		result |= inv_iam20680_write_reg(s, MPUREG_LP_MODE_CFG, 1, &d);
	} else {
		if (lp_mode == ST_GYRO_LP_MODE)
			d = DEF_SELFTEST_SAMPLE_RATE_LP;
		else
			d = DEF_SELFTEST_SAMPLE_RATE;
		result |= inv_iam20680_write_reg(s, MPUREG_SMPLRT_DIV, 1, &d);
	}

	/* wait for the sampling rate change to stabilize */
	inv_iam20680_sleep_us(GYRO_ENGINE_UP_TIME*1000);

	/* config accel LPF register */
	if (lp_mode == ST_ACCEL_LP_MODE)
		d = BIT_A_DLPF_CFG_MASK;
	else
		d = DEF_ST_ACCEL_LPF;
	result |= inv_iam20680_write_reg(s, MPUREG_ACCEL_CONFIG_2, 1, &d);
	
    /* Gyro full scale range set to +/- 250 dps */
	d = self_test_flag | DEF_SELFTEST_GYRO_FS;
	result |= inv_iam20680_write_reg(s, MPUREG_GYRO_CONFIG, 1, &d);

	/* Accel full scale range set to +/- 2g */
	d = self_test_flag | DEF_SELFTEST_ACCEL_FS;
	result |= inv_iam20680_write_reg(s, MPUREG_ACCEL_CONFIG, 1, &d);

	/* accel lp mode */
	dd = CLK_SEL;
	if (lp_mode == ST_ACCEL_LP_MODE)
		dd |= BIT_ACCEL_CYCLE_MASK;
	result |= inv_iam20680_write_reg(s, MPUREG_PWR_MGMT_1, 1, &dd);

	/* wait for the output to get stable */
	inv_iam20680_sleep_us(DEF_ST_STABLE_TIME*1000);

	/* enable sensor output to FIFO */
	d = BIT_GYRO_FIFO_EN_MASK | BIT_ACCEL_FIFO_EN_MASK;
	for (i = 0; i < THREE_AXES; i++) {
		gyro_result[i] = 0;
		accel_result[i] = 0;
	}

	ss = 0;
	while(ss < 200) {

		/* clear FIFO + enable FIFO reading */
		da = BIT_FIFO_RST_MASK | BIT_FIFO_EN_MASK;
		result |= inv_iam20680_write_reg(s, MPUREG_USER_CTRL, 1, &da);

		result |= inv_iam20680_write_reg(s, MPUREG_FIFO_EN, 1, &d);

		if (lp_mode)
			inv_iam20680_sleep_us(DEF_GYRO_WAIT_TIME_LP*1000);
		else
			inv_iam20680_sleep_us(DEF_GYRO_WAIT_TIME*1000);

		/* stop FIFO */
		tmp = 0;
		result |= inv_iam20680_write_reg(s, MPUREG_FIFO_EN, 1, &tmp);

		result |= inv_iam20680_read_reg(s, MPUREG_FIFO_COUNTH, FIFO_COUNT_BYTE, data);

		fifo_count = (data[0] << 8) | data[1];
		packet_count = fifo_count / packet_size;
		
		if (packet_count == 0) {				// If the FIFO is empty
            /* To avoid indefinitely waiting for FIFO data, we return ERROR_HW if data is not received on FIFO for more than 1 sec */
            number_times_fifo_empty++;
            if (number_times_fifo_empty == fifo_reads_per_second)		// If the FIFO has been empty for one second (or fifo_reads_per_second reads).
	            return INV_ERROR_HW;									// Then we assume the FIFO is not filling and return an error.
            continue;													// Otherwise keep going.
            } else {
            number_times_fifo_empty = 0;
		}
		
		i = 0;
		while ((i < packet_count) && (ss < 200)) {
			short vals[3];
			result |= inv_iam20680_read_reg(s, MPUREG_FIFO_R_W, packet_size, data);
			ind = 0;
			for (j = 0; j < THREE_AXES; j++) {
				vals[j] = (data[ind + 2 * j] << 8) | data[ind + 2 * j + 1];
				accel_result[j] += vals[j];
			}
			ind += BYTES_PER_SENSOR;
			for (j = 0; j < THREE_AXES; j++) {
				vals[j] = (data[ind + 2 * j] << 8) | data[ind + 2 * j + 1];
				gyro_result[j] += vals[j];
			}
			ss++;
			i++;
		}
	} //while(ss < 200)

	for (j = 0; j < THREE_AXES; j++) {
		accel_result[j] = accel_result[j] / ss;
		gyro_result[j] = gyro_result[j] / ss;
	}


	/* Disable ACCEL Lp Mode */
	if (lp_mode == ST_ACCEL_LP_MODE) {
		result |= inv_iam20680_read_reg(s, MPUREG_PWR_MGMT_1, 1, &d);
		d &= ~BIT_ACCEL_CYCLE_MASK;
		result |= inv_iam20680_write_reg(s, MPUREG_PWR_MGMT_1, 1, &d);
	}

	return result;
}


int inv_iam20680_run_selftest(struct inv_iam20680 * s)
{
	int result = 0;
	int gyro_ln_bias_st[THREE_AXES],gyro_ln_bias[THREE_AXES];
	int accel_ln_bias_st[THREE_AXES],accel_ln_bias[THREE_AXES];
	int test_times;
	char accel_result, gyro_result;
	
	struct recover_regs recover_regs;
	uint8_t data;

	result |= save_settings(s, &recover_regs);

	/* enable sensors */
	data = 0;
	result |= inv_iam20680_write_reg(s, MPUREG_PWR_MGMT_2, 1, &data);
	inv_iam20680_sleep_us(GYRO_ENGINE_UP_TIME*1000); // 50 ms 

	accel_result = 0;
	gyro_result = 0;

	/* (1) hardware self-test */
	/* Collect averaged data of gyro and accel in normal mode (LN mode set, self-test not set).
	   Try up to DEF_ST_TRY_TIMES times in case of some error such as I2C error.
	   The collected data can be utilized as factory bias of normal mode.
	   Will be checked later.*/
	test_times = DEF_ST_TRY_TIMES;
	while (test_times > 0) {
		result = do_test(s, 0, gyro_ln_bias, accel_ln_bias, ST_NORMAL_MODE);
		if (result)
			test_times--;
		else
			break;
	}
	if (result)
		goto test_fail;

	/* (2) hardware self-test */
	/* Collect averaged data of gyro and accel in hardware selftest mode.(LN mode set, self-test set)
	   Try up to DEF_ST_TRY_TIMES times in case of some error such as I2C error.
	   Will be checked later */
	test_times = DEF_ST_TRY_TIMES;
	while (test_times > 0) {
		result = do_test(s, (BIT_XG_ST_MASK | BIT_YG_ST_MASK | BIT_ZG_ST_MASK), gyro_ln_bias_st, accel_ln_bias_st, ST_NORMAL_MODE);
		if (result)
			test_times--;
		else
			break;
	}
	if (result)
		goto test_fail;

	/* Check data collected in step (1) and (2).
	   Compare with OTP values which are stored at factory */
	accel_result = !check_accel_self_test(s, accel_ln_bias, accel_ln_bias_st);
	gyro_result = !check_gyro_self_test(s, gyro_ln_bias, gyro_ln_bias_st);


test_fail:
	recover_settings(s, &recover_regs);

	return (accel_result << 1) | gyro_result;
}

int inv_iam20680_run_factory_calib(struct inv_iam20680 * s)
{
	int result = 0;
	int gyro_lp_bias[THREE_AXES], accel_lp_bias[THREE_AXES];
	int gyro_ln_bias[THREE_AXES],accel_ln_bias[THREE_AXES];

	int test_times;

	int i;
	struct recover_regs recover_regs;
	uint8_t data;

	result |= save_settings(s, &recover_regs);

	/* enable sensors */
	data = 0;
	result |= inv_iam20680_write_reg(s, MPUREG_PWR_MGMT_2, 1, &data);
	inv_iam20680_sleep_us(GYRO_ENGINE_UP_TIME*1000);

    /* (1) Bias collection for accel,gyro LN mode */
	/* Collect averaged data of gyro and accel in normal mode ( LN mode ).
	   Try up to DEF_ST_TRY_TIMES times in case of some error such as I2C error.
	   The collected data can be utilized as factory bias of normal mode.
	   Will be checked later.*/
	test_times = DEF_ST_TRY_TIMES;
	while (test_times > 0) {
		result = do_test(s, 0, gyro_ln_bias, accel_ln_bias, ST_NORMAL_MODE);
		if (result)
			test_times--;
		else
			break;
	}
	if (result)
		goto test_fail;

	for (i = 0; i < 3; i++) {
		/* saving values to calculate bias later */
		s->gyro_ln_bias[i] = gyro_ln_bias[i] ;
		s->accel_ln_bias[i] = accel_ln_bias[i];
	}

	/** Collect LP bias to calculate bias **/	

	/* (3) Bias collection for accel lp mode */
	/* Collect averaged accel data in lp mode.
	   Try up to DEF_ST_TRY_TIMES times in case of some error such as I2C error.
	   This is only for factory bias of accel lp mode */
	test_times = DEF_ST_TRY_TIMES;
	while (test_times > 0) {
		result = do_test(s, 0, gyro_lp_bias, accel_lp_bias, ST_ACCEL_LP_MODE);
		if (result)
			test_times--;
		else
			break;
	}
	if (result)
		goto test_fail;

	for (i = 0; i < 3; i++) {
		s->accel_lp_bias[i] = accel_lp_bias[i] ;
	}

	/* (4) Bias collection for gyro lp mode */
	/* Collect averaged gyro data in lp mode.
	   Try up to DEF_ST_TRY_TIMES times in case of some error such as I2C error.
	   This is only for factory bias of gyro lp mode */
	test_times = DEF_ST_TRY_TIMES;
	while (test_times > 0) {
		result = do_test(s, 0, gyro_lp_bias, accel_lp_bias, ST_GYRO_LP_MODE);
		if (result)
			test_times--;
		else
			break;
	}
	if (result)
		goto test_fail;

	for (i = 0; i < 3; i++) {
		s->gyro_lp_bias[i] = gyro_lp_bias[i] ;
	}

test_fail:
	recover_settings(s, &recover_regs);

	return result;
}

void inv_iam20680_get_scaled_bias(struct inv_iam20680 * s, int * raw_gyro_bias,int *raw_accel_bias)
{
	int axis, axis_sign;
	int gravity;
	int i, t;
	int check;
	int scale;

	/* check bias there ? */
	check = 0;
	for (i = 0; i < 3; i++) {
		if (s->gyro_ln_bias[i] != 0)
			check = 1;
		if (s->gyro_lp_bias[i] != 0)
			check = 1;
		if (s->accel_ln_bias[i] != 0)
			check = 1;
		if (s->accel_lp_bias[i] != 0)
			check = 1;
	}

	/* if no bias, return all 0 */
	if (check == 0) {
		for (i = 0; i < 6; i++) {
			raw_gyro_bias[i] = 0;
			raw_accel_bias[i] = 0;
		}
		return;
	}

	/* dps scaled by 2^16 */
	scale = 65536 / DEF_SELFTEST_GYRO_SENS;

	/* Gyro LN mode */
	t = 0;
	for (i = 0; i < 3; i++)
	raw_gyro_bias[i + t] = s->gyro_ln_bias[i] * scale;

	/* Gyro LP mode */
	t += 3;
	for (i = 0; i < 3; i++)
	raw_gyro_bias[i + t] = s->gyro_lp_bias[i] * scale;

	axis = 0;
	axis_sign = 1;
	if (INV_ABS(s->accel_ln_bias[1]) > INV_ABS(s->accel_ln_bias[0]))
		axis = 1;
	if (INV_ABS(s->accel_ln_bias[2]) > INV_ABS(s->accel_ln_bias[axis]))
		axis = 2;
	if (s->accel_ln_bias[axis] < 0)
		axis_sign = -1;

	/* gee scaled by 2^16 */
	scale = 65536 / (DEF_ST_SCALE / (DEF_ST_ACCEL_FS_MG / 1000));

	gravity = 32768 / (DEF_ST_ACCEL_FS_MG / 1000) * axis_sign;
	gravity *= scale;

	/* Accel LN mode */
	t = 0 ;
	for (i = 0; i < 3; i++) {
		raw_accel_bias[i + t] = s->accel_ln_bias[i] * scale;
		if (axis == i)
			raw_accel_bias[i + t] -= gravity;
	}

	/* Accel LP mode */
	t += 3;
	for (i = 0; i < 3; i++) {
		raw_accel_bias[i + t] = s->accel_lp_bias[i] * scale;
		if (axis == i)
			raw_accel_bias[i + t] -= gravity;
	}
}

void inv_iam20680_apply_offset(struct inv_iam20680 * s, int isAccelLpMode, int isGyroLpmode)
{
	/* Device struct holds LN and LP offset, based on the pwr mode offset registers need to be updated */
	int ii,t = 0;
	uint8_t reg_addr ;
	uint8_t	data;

	/** Applying Gyro offset **/
	reg_addr = MPUREG_XG_OFFS_USRH;
	if ( isGyroLpmode )
		t = 3;
	else
		t = 0;
	for (ii = 0; ii < 3; ii++) {
		data = (s->gyro_offset[ii+t] & 0xFF00) >> 8;
		inv_iam20680_write_reg(s, reg_addr++, 1, &data);
		data = s->gyro_offset[ii+t] & 0x00FF;
		inv_iam20680_write_reg(s, reg_addr++, 1, &data);			
	}
	
	/** Applying Accel offset **/
	reg_addr = MPUREG_XA_OFFSET_H;
	if ( isAccelLpMode )
		t = 3;
	else
		t = 0;
			
	for (ii = 0; ii < 3; ii++) {
		data = (s->accel_offset[ii+t] & 0xFF00) >> 8;							// Take high order byte
		inv_iam20680_write_reg(s, reg_addr++, 1, &data);
		
		data = s->accel_offset[ii+t]  & 0x00FE;									// Only take the high order 7 bits
		inv_iam20680_write_reg(s, reg_addr++, 1, &data);
		reg_addr++;                                                             // Skip over unused register
	}
}

void inv_iam20680_compute_offset(struct inv_iam20680 * s)
{
	int axis, axis_sign;
	int gravity,i;
	int offset,lpoffset;
	
	/** Compute Gyro Offset **/
	for (i = 0; i < 3; i++) {
		// Change to 2's complement and convert from 250 dps to 1000dps (>>2)
		s->gyro_offset[i] = -1 * ( s->gyro_ln_bias[i]  >> 2);
		s->gyro_offset[i+3] = -1 * (s->gyro_lp_bias[i] >> 2);   //LP
	}
	
	/** Compute Accel Offset from raw bias collected in factory calibration**/
	axis = 0;
	axis_sign = 1;
	
	if (INV_ABS(s->accel_ln_bias[1]) > INV_ABS(s->accel_ln_bias[0]))
		axis = 1;
	if (INV_ABS(s->accel_ln_bias[2]) > INV_ABS(s->accel_ln_bias[axis]))
		axis = 2;
	if (s->accel_ln_bias[axis] < 0)
		axis_sign = -1;
	
	gravity = (32768 / (DEF_ST_ACCEL_FS_MG / 1000)) * axis_sign;
	
	for (i = 0; i < 3; i++) {

		offset = s->accel_ln_bias[i] ;
		lpoffset = s->accel_lp_bias[i] ;
		
		/* Remove Gravity from axis **/
		if (axis == i) {
			offset -= gravity;
			lpoffset -= gravity;   //LP
		}
		// convert from 2g to 16g (1LSB = 0.49mg) on 15bits register and mask bit0
		// note : there is no need to shift the register value as the register is 0.98mg steps
		s->accel_offset[i] = (int16_t) (( s->accel_trim_offset[i] -( offset  >> 3))& ~1 );
		s->accel_offset[i + 3] = (int16_t) ((s->accel_trim_offset[i] - (lpoffset  >> 3)) & ~1 ) ;
		
	}
}

void inv_iam20680_get_trim_offset(struct inv_iam20680 * s)
{
	uint8_t reg_addr ,ii;
	uint8_t	data;
	reg_addr = MPUREG_XA_OFFSET_H;
	for (ii = 0; ii < 3; ii++) {
		inv_iam20680_read_reg(s, reg_addr++, 1, &data);				// Get current offset value (16 bits in two registers)
		s->accel_trim_offset[ii] = data << 8;
		inv_iam20680_read_reg(s, reg_addr++, 1, &data);
		s->accel_trim_offset[ii] += data;
		reg_addr++;
	}
}

void inv_iam20680_set_trim_offset(struct inv_iam20680 * s)
{
	int ii;
	uint8_t reg_addr ;
	uint8_t	data;
	
	/** Applying Gyro trim offset **/
	reg_addr = MPUREG_XG_OFFS_USRH;
	for (ii = 0; ii < 3; ii++) {
		data = 0;
		inv_iam20680_write_reg(s, reg_addr++, 1, &data);
		inv_iam20680_write_reg(s, reg_addr++, 1, &data);
	}
	
	/** Applying accel trim offset **/
	reg_addr = MPUREG_XA_OFFSET_H;
	for (ii = 0; ii < 3; ii++) {
		data = (s->accel_trim_offset[ii]) >> 8;							// Take high order byte
		inv_iam20680_write_reg(s, reg_addr++, 1, &data);
		
		data = (s->accel_trim_offset[ii]) & 0x00FE;						// Only take the high order 7 bits
		inv_iam20680_write_reg(s, reg_addr++, 1, &data);
		reg_addr++;
	}
}