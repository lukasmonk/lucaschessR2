#pragma once

enum eTimeData { W_TIME, B_TIME, W_INC, B_INC, TIME, INC, MOVES_TO_GO, MOVE_TIME, 
	             MAX_NODES, MAX_DEPTH, FLAG_INFINITE, SIZE_OF_DATA };

struct sTimer {
private:
    int data[SIZE_OF_DATA]; // various data used to set actual time per move (see eTimeData)
    int startTime;          // when we have begun searching
    int iterationTime;      // when we are allowed to start new iteration
    int moveTime;           // basic time allocated for a move
public:
    void Clear(void);
    void SetStartTime();
    void SetMoveTiming(void);
    void SetIterationTiming(void);
    int FinishIteration(void);
    int GetMS(void);
    int GetElapsedTime(void);
    int IsInfiniteMode(void);
    int TimeHasElapsed(void);
    int GetData(int slot);
    void SetData(int slot, int val);
    void SetSideData(int side);
};

extern sTimer Timer;
