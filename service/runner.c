#define _GNU_SOURCE
#include <sys/mman.h>
#include <seccomp.h>
#include <unistd.h>
#include <assert.h>
#include <unistd.h>
#include <string.h>

int main()
{
	char cwd[1024];
	uid_t ruid, euid, suid;
	gid_t rgid, egid, sgid;
	getresuid(&ruid, &euid, &suid);
	getresgid(&rgid, &egid, &sgid);
	assert(ruid != 0);
	assert(euid != 0);
	assert(suid != 0);
	assert(rgid != 0);
	assert(egid != 0);
	assert(sgid != 0);
	getcwd(cwd, 1024);
	assert(strcmp(cwd, "/") == 0);


	void *shellcode_addr = mmap(0, 0x1000, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE|MAP_ANON, 0, 0);
	assert(shellcode_addr != MAP_FAILED);
	read(0, shellcode_addr, 0x1000);

	//scmp_filter_ctx ctx;
	//ctx = seccomp_init(SCMP_ACT_KILL);
	//assert(seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(open), 0) == 0);
	//assert(seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0) == 0);
	//assert(seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0) == 0);
	//assert(seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0) == 0);
	//assert(seccomp_load(ctx) == 0);

	((void(*)())shellcode_addr)();
}
