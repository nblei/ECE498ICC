#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <pigpio.h>
#include <unistd.h>

#define TARGET_FREQ 640000

#define GPIO_ERR(_pin) do {fprintf(stderr, "GPIO error on pin %d\\n", _pin); exit(1);} while(0)

#define DCLK  4

#define DIN8  26
#define DIN7  21
#define DIN6  20
#define DIN5  16
#define DIN4  12
#define DIN3  1
#define DIN2  7
#define DIN1  8
#define DIN0  25

#define DOUT0 14
#define DOUT1 15
#define DOUT2 18
#define DOUT3 17
#define DOUT4 27
#define DOUT5 22


#define START_ALE DOUT0
#define READ DOUT1
#define ADDR_A DOUT5
#define ADDR_B DOUT4
#define ADDR_C DOUT3

#define EOC DIN8

static int DIN[] = {DIN0, DIN1, DIN2, DIN3, DIN4, DIN5, DIN6, DIN7, DIN8};
static int DOUT[] = {DOUT0, DOUT1, DOUT2, DOUT3, DOUT4, DOUT5};

int set_gpio_inputs(void)
{
	for (int i = 0; i < sizeof(DIN)/sizeof(DIN[0]); ++i) {
		if (0 != gpioSetMode(DIN[i], PI_INPUT)) {
			fprintf(stderr, "Unable to set %d as GPIO Input\n", DIN[i]);
			exit(1);
		}
	}
	return 0;
}

int set_gpio_outputs(void)
{
	for (int i = 0; i < sizeof(DOUT) / sizeof(DOUT[0]); ++i) {
		if (0 != gpioSetMode(DOUT[i], PI_OUTPUT)) {
			fprintf(stderr, "Unable to set %d as GPIO Output\n", DIN[i]);
			exit(1);
		}
	}
	return 0;
}

unsigned char read_809(void)
{
	int rv;
	unsigned char retval = 0;

	for (int i = 0; i < 8; ++i) {
		if (PI_BAD_GPIO == (rv = gpioRead(DIN[i]))) GPIO_ERR(DIN[i]);
		retval |= rv << i;
	}
	return retval;
}


int start_clock(unsigned freq)
{
	int rv;
	switch (rv = gpioHardwareClock(DCLK, 640000)) {
		case 0:
			break;
		case PI_BAD_GPIO:
			fprintf(stderr, "Bad GPIO\n");
			break;
		case PI_NOT_HCLK_GPIO:
			fprintf(stderr, "Not HCLKC GPIO\n");
			break;
		case PI_BAD_HCLK_FREQ:
			fprintf(stderr, "Unable to use freq\n");
			break;
		case PI_BAD_HCLK_PASS:
		      	fprintf(stderr, "PI_BAD_HCLK_PASS\n");
		default:
		      fprintf(stderr, "Unknown error on gpioHardwareClock\n");
		      break;
	}
	return rv;
}

int stop_clock(void)
{
	return start_clock(0);
}

void set_channel(uint8_t channel)
{
	int pina, pinb, pinc;
	pina = channel & 1;
	pinb = (channel >> 1) & 1;
	pinc = (channel >> 2) & 1;
	if (0 != gpioWrite(ADDR_A, pina)) GPIO_ERR(ADDR_A);
	if (0 != gpioWrite(ADDR_B, pinb)) GPIO_ERR(ADDR_B);
	if (0 != gpioWrite(ADDR_C, pinc)) GPIO_ERR(ADDR_C);
}

unsigned char read_adc(uint8_t channel)
{
	// Send Start/ALE
	unsigned char retval = 69;
	int rv;
	set_channel(channel);
	if (0 != (rv = gpioTrigger(START_ALE, 2, 1))) {
		fprintf(stderr, "gpioTrigger returned %d\n", rv);
		gpioTerminate();
		exit(1);
	}
	// Wait for EOC to go low
	if (0 != usleep(4)) {
		perror("usleep");
		exit(1);
	}
	//assert(!gpioRead(EOC));

	// Poll on EOC until high
	while (!gpioRead(EOC)) ;

	if (0 != gpioWrite(READ, 1)) { GPIO_ERR(READ); }
	retval = read_809();
	if (0 != gpioWrite(READ, 0)) { GPIO_ERR(READ); }


	return retval;
}

int main(int argc, char * argv[])
{
	if (argc == 1 || argc > 9) {
		fprintf(stderr, "usage: %s <1 or more inputs used>\n",
				argv[0]);
		exit(1);
	}

	int arr[8] = {0};
	for (int a = 1; a < argc; ++a) {
		int idx = atoi(argv[a]);
		assert(idx >= 0);
		assert(idx < 8);
		arr[idx] = 1;
	}

	if (PI_INIT_FAILED == gpioInitialise()) {
		fprintf(stderr, "Unable to initialize pigpio\n");
		gpioTerminate();
		exit(1);
	}
	else {
		; //printf("pigpio intialized\n");
	}

	//printf("\033[2J");

	//stop_clock();
	if (start_clock(TARGET_FREQ) != 0) {
		exit(1);
	}

	set_gpio_inputs();
	set_gpio_outputs();
	//printf("DCLK mode: %d\n", gpioGetMode(DCLK));
	//printf("INPUT: %d\nOUTPUT: %d\n", PI_INPUT, PI_OUTPUT);

	int channel = 3;
	float vcc = 3.21;
	float vgrnd = 0.0;
	float vdif = (vcc - vgrnd) / 255.0f;

	//for (;1;) {
		volatile unsigned char results[8];
		for (int i = 0; i <= 7; ++i) {
			if (arr[i] == 0) continue;
			results[i] = read_adc(i);
			printf("%d:%d\n", i, results[i]);
		}
		//usleep(250000);
		//++channel;
		//channel &= 7;
	//}

	stop_clock();
	gpioTerminate();

	return 0;
}
