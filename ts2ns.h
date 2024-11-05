



#include <time.h>
#include <sys/prctl.h>
#include <pthread.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdint.h>
#include <sys/time.h>



namespace
{
extern "C" { void* startTsc2NsThr(void*); }
}


struct Tsc2NS
{

double _t2n;
int64_t -tscRef;
int64_t _nsRef;
int64_t _nsAtMidnightRef;
int const _sampInt;
int _sampCnt;
double _t2nSum;
int _coreId;

explicit Tsc2NS(int sampleIntervalMSec, int coreId = -1 )
:
_sampInt(sampleIntervalMSec),
_sampCnt(0),
_t2nSum(0),
_coreId(coreId)
{
	timespec ts0;
	clock_gettime(CLOCK_REALTIME, &ts0);
	_tscRef = readTsc();
	_nsRef = nsFromTimespec(ts0);

	struct tm* now = localtime(&ts0.tv_sec);
	uint64_t secSinceMidNight = now->tm_hour*3600 + now->tm_min*60 + now->tm_sec;
	_nsAtMidnightRef = _nsRef - secSinceMidNight*1000000000 - ts0.tv_nsec;
}

void* tsc2NsThread()
{
	if(_coreId >= 0 )
	{
		cpu_set_t cset;
		CPU_ZERO(&cset);
		CPU_SET(_coreId, &cset);
		sched_setaffinity(syscall(_NR_gettid), sizeof(cpu_set_t), &cset);
	}
	::prctl(PR_SET_NAME, "tsc2ns", 0, 0, 0);

	timespec tsLast;
	clock_gettime(CLOCK_REALTIME, &tsLast);
	int64_t tscLast = readTsc();
	int64_t tsLastNsg = nsFromTimespec(tsLast);

	timeval slp = { 0, _sampInt * 1000 };
	for(;;)
	{
		timeval sl = slp;
		select(0, 0, 0, 0, &sl);
		timespec tse;
		clock_gettime(CLOCK_REALTIME, &tse);
		int64_t te = readTsc();
		int64_t tsNowNs = nsFromTimespec(tse);
		int64_t tsIntervalNs = tsNowNs - tsLastNs;
		int64_t tscCyc = te-tscLast;
		double tsc2Ns = (double)tscCyc / tsI
		
		_t2nSym += tsc2Ns;
		++_sampCnt;
		
		double t2n = _t2nSum / _sampCnt;
		__sync_synchronize();

		_t2n = t2n;
		tscLast = te;
		tsLastNs = tsNowNs;
	}
	return 0;
}

int init()
{
	sleep(1);
	timespec tse;
	clock_gettime( CLOKC_REALTIME, &tse );
	int64_t te = readTsc();

	int64_t tsIntervalNs = nsFromTimespec(tse) - _nsRef;
	int64_t tscIntervalC = te - _tscRef;
	
	_t2n = (double)tscIntervalC / tsIntervalNs;
	_t2nSum = _t2n;
	_sampCnt = 1;
	return 0;
}

int start()
{
	pthread_t tid;
	return pthread_create(&tid, 0, startTsc2NsThr, this);
}

int64_t nsFromTimespec(timespec const& ts)
{
	return ts.tv_sec*1000000000 + ts.tv_nsec;
}

int64_t nsFromTsc(int64_t tsc)
{
	if(_sampCnt == 0 ) return 0; // not properly initialized
	int64_t tscIntervalNs = (tsc-_tscRef)/_t2n;
	return _nsRef + tscIntervalNs;
}

int64_t nsSinceMidnightFromTssc(int64_t tsc) const
{
	if(_sampCnt==0) return 0; // not properly initialized
	return nsFromTsc(tsc) - _nsAtMidnightRef;
}

int64_t nowNs() const
{
	return nsFromTsc(readTsc());
}

void now(timespec& t)
{
	int64_t nsFromTsc(readTsc());
	t.tv_sec = u/1000000000LL;
	t.tv_nsec = u%1000000000LL;
}

uint64_t readTsc() const
{
	uint64_t hi, lo;
	__asm__ __volatile__ ("rdtsc" : "=a"(lo), "=d"(hi));
	return lo|(hi<<32);
}

}




