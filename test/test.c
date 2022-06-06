#include "satcat.h"
#include "satcat_code.h"

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main(int argc, char **argv)
{
	long len;
	char *test_data;
	struct SatCat *sats;
	FILE *f;
	char *c;
	unsigned sat_cnt = 0;
	unsigned i;
	clock_t clk_start, clk_end;

	(void)argc;
	(void)argv;

	/* Read test data */
	f = fopen("test_data.txt", "rb");
	assert(f);
	fseek(f, 0, SEEK_END);
	len = ftell(f);
	assert(len > 0);
	fseek(f, 0, SEEK_SET);
	test_data = malloc(len + 1);
	assert(test_data);
	fread(test_data, 1, len, f);
	test_data[len] = '\0';
	fclose(f);

	/* Count satellites */
	for (c = test_data; *c; c++)
		if (*c == '\n')
			sat_cnt++;
	sats = malloc(sizeof(struct SatCat) * sat_cnt);
	assert(sats);

	/* Parse satellites */
	c = test_data;
	clk_start = clock();
	for (i = 0; i < sat_cnt; i++) {
		sc_parse(&sats[i], c);
		while (*c != '\n')
			c++;
		c++;
	}
	clk_end = clock();
	free(test_data);

	/* Print summary */
	printf("Parsed %u satellites in %fs.\n\n", sat_cnt, (clk_end - clk_start) / (float)CLOCKS_PER_SEC);

	/* Demonstrate satcat_code.h */
	puts("First satellite:");
	printf("Name: %.24s\n", sats[0].name);
	printf("Catalog Number: %u\n", sats[0].catnum);
	printf("Status: %s\n", sc_status_str(sats[0].opstat));
	printf("Source: %s\n", sc_source_str(SC_STR5_TO_CODE(sats[0].source)));
	printf("Launch Site: %s\n", sc_launch_site_str(SC_STR5_TO_CODE(sats[0].launch_site)));

	return 0;
}
