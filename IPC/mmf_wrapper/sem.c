#include <fcntl.h>
#include <semaphore.h>
#include <stdio.h>
#include<stdlib.h>
#include<unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <sys/mman.h>

#define POOL_SIZE 50
#define NAME_SIZE 20
sem_t* semaphore_pool[POOL_SIZE];
char semaphore_name[POOL_SIZE][NAME_SIZE];
void* mmf_pool[POOL_SIZE];
char mmf_name[POOL_SIZE][NAME_SIZE];
char* read_buff[POOL_SIZE];
// Number of semaphores currently allocated
int semaphore_count=0;
// Number of mmf currently allocated
int mmf_count=0;

// Implementation of itoa function of C. Intention for reimplementation unclear.
char* itoa(int sum){
	if(sum>=0){
		int i=0;
		char* temp=(char*)malloc(20);
		char* msg=(char*)malloc(20);
		while(sum>0){
			temp[i]=sum%10+'0';
			sum=sum/10;
			i++;
		}
		*(msg+i+1)='\0';
		int mmf_pool=0;
		for(int j=i; j>=1; j--){
			 *(msg+j)=temp[mmf_pool];
			 mmf_pool++;
		}
		*msg='0';
		free(temp);
		return msg;
	}
	else{
		sum=-sum;
		char* temp=(char*)malloc(20);
		char* msg=(char*)malloc(20);
		int i=0;
		while(sum>0){
			temp[i]=sum%10+'0';
			sum=sum/10;
			i++;
		}
		*(msg+i+1)='\0';
		int mmf_pool=0;
		for(int j=i; j>=1; j--){
			 *(msg+j)=temp[mmf_pool];
			 mmf_pool++;
		}
		*msg='1';
		free(temp);
		return msg;
	}
}


int is_open(char name[], char type[]){

    if(strcmp(type, "sem") == 0){
        for(int i=0; i<POOL_SIZE; i++){
            if(strcmp(semaphore_name[i], name) == 0) return i;
        }
        return -1;
    }
    else if(strcmp(type, "mmf") == 0){
        for(int i=0; i<POOL_SIZE; i++){
            if(strcmp(mmf_name[i], name) == 0) return i;
        }
        return -1;
    }
    else{
        return -1;
    }
}

int semaphore_open(char name[NAME_SIZE], int oflag, unsigned int val){
    int idx = is_open(name, "sem");
    if(idx == -1){
	    semaphore_pool[semaphore_count] = sem_open(name, oflag, 0666, val);
	    sem_unlink(name);
	    strcpy(semaphore_name[semaphore_count], name);
	    semaphore_count++;
	    return semaphore_count-1;
	}
	else{
	    return idx;
	}
}

int getO_Creat(){
	return O_CREAT;
}

void wait(int ind){
	sem_wait(semaphore_pool[ind]);
}

void post(int ind){
	sem_post(semaphore_pool[ind]);
}

int getO_CREAT_ORDWR(){
	return O_CREAT | O_RDWR;
}

int shared_mem_open(char name[], int shm_flag){
	return shm_open(name, shm_flag, 0666);
}

void ftrunc(int shm_fd, const int size){
	ftruncate(shm_fd, size);
}

int mmap_obj(int size, int shm_fd){
	mmf_pool[mmf_count]=mmap(0, size, PROT_WRITE | PROT_READ, MAP_SHARED, shm_fd, 0);
	mmf_count++;
	return mmf_count-1;
}

int shared_mem(char name[NAME_SIZE], int size){
    int idx = is_open(name, "mmf");
    if(idx==-1){
        int handle = shm_open(name, O_CREAT | O_RDWR, 0666);
        ftruncate(handle, size);
        mmf_pool[mmf_count] = mmap(0, size, PROT_WRITE | PROT_READ, MAP_SHARED, handle, 0);
        strcpy(mmf_name[mmf_count], name);
        mmf_count++;
        return mmf_count-1;
	}
	else{
	    return idx;
	}
}

void unlinkSHM(char* name){
  shm_unlink(name);
}

void writeMMF(char msg[], int mmap){
	sprintf(mmf_pool[mmap], "%s", msg);
}

char* readMMF(int mmap){
    return (char*)mmf_pool[mmap];
}

void memfree(int mmap){
	free(read_buff[mmap]);
}

void mywrite(char* src, char* dst){
	int i=0;
	while(*(src+i)!='\0'){
		*(dst+i)=*(src+i);
		i++;
	}
	*(dst+i)='\0';
}

void WriteInt(int val, int mmap){
	char* arr=itoa(val);
	mywrite(arr, mmf_pool[mmap]);
	free(arr);
}

int ReadInt(int mmap){
	if(*(char*)mmf_pool[mmap]=='0')
		return atoi((char*)(mmf_pool[mmap]+1));
	else
		return -atoi((char*)(mmf_pool[mmap]+1));
}

int getVal(int sem){
  int val;
  sem_getvalue(semaphore_pool[sem], &val);
  printf("sem value is %d and sem index is %d\n", val, sem);
  return val;
}

void reset(){
  for(int i=0; i<semaphore_count; i++){
    int val;
    sem_getvalue(semaphore_pool[i], &val);
    printf("%d\n", val);
    sem_destroy(semaphore_pool[i]);
  }
  semaphore_count=0;
  mmf_count=0;
}

//int pinet_img_lock = -1;
//int pinet_img_mmf = -1;
//int pinet_output_lock = -1;
//int pinet_output_mmf = -1;
//int pinet_output_ready_lock = -1;
//int pinet_output_ready_mmf = -1;
//
//void init_pinet_ipc(){
//    pinet_img_lock = semaphore_open("pinet_img_lock", O_CREAT, 1);
//    pinet_output_lock = semaphore_open("pinet_output_lock", O_CREAT, 1);
//    pinet_output_ready_lock = semaphore_open("pinet_output_ready_lock", O_CREAT, 1);
//
//    pinet_img_mmf = shared_mem("pinet_img_mmf", 1000000);
//    pinet_output_mmf = shared_mem("pinet_output_mmf", 1024);
//    pinet_output_ready_mmf = shared_mem("pinet_output_ready_mmf", 4);
//
//    printf("%d\n", semaphore_count);
//    getVal(pinet_img_lock);
//    getVal(pinet_output_lock);
//    getVal(pinet_output_ready_lock);
//}
//
//char* read_pinet_img(){
//    wait(pinet_img_lock);
//    char* output =  readMMF(pinet_img_mmf, 1000000);
//    post(pinet_img_lock);
//    return output;
//}
//
//void write_pinet_img(char img[]){
//    wait(pinet_img_lock);
//    writeMMF(img, pinet_img_mmf);
//    post(pinet_img_lock);
//}
//
//char* read_pinet_output(){
//    wait(pinet_output_lock);
//    char* output =  readMMF(pinet_output_mmf, 1024);
//    post(pinet_output_lock);
//    return output;
//}
//
//void write_pinet_output(char output[]){
//    getVal(pinet_output_lock);
//    wait(pinet_output_lock);
//    getVal(pinet_output_lock);
//    writeMMF(output, pinet_output_mmf);
//    post(pinet_output_lock);
//}
//
//int is_pinet_output_ready(){
//    getVal(pinet_output_ready_lock);
//    wait(pinet_output_ready_lock);
//    getVal(pinet_output_ready_lock);
//    int output =  ReadInt(pinet_output_ready_mmf, 4);
//    post(pinet_output_ready_lock);
//    return output;
//}
//
//void set_pinet_output_ready(){
//    getVal(pinet_output_ready_lock);
//    wait(pinet_output_ready_lock);
//    getVal(pinet_output_ready_lock);
//    WriteInt(1, pinet_output_ready_mmf);
//    post(pinet_output_ready_lock);
//}
//
//void unset_pinet_output_ready(){
//    wait(pinet_output_ready_lock);
//    WriteInt(0, pinet_output_ready_mmf);
//    post(pinet_output_ready_lock);
//}

int main(){
//    int i = shared_mem("Hello", 5);
//    int j = shared_mem("Hello", 5);
//    char* x = readMMF(i);
//    printf("%s\n", x);
//    int k = semaphore_open("World", O_CREAT, 1);
//    int l = semaphore_open("World", O_CREAT, 1);
//    printf("%d %d\n", k, l);
//    return 0;
}
