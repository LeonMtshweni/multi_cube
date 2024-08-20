# this function writes the slurm/bash script 
def write_slurm(bash_filename,
                jobname,
                logfile,
                cmd,
                email_address,
                time='72:00:00',  
                partition='Main',
                ntasks='1',
                nodes='1',
                cpus='32',
                mem='128GB'):

    f = open(bash_filename,'w')
    f.writelines(['#!/bin/bash\n',
        '#file: '+bash_filename+':\n',
        '#SBATCH --job-name='+jobname+'\n',
        '#SBATCH --time='+time+'\n',
        '#SBATCH --partition='+partition+'\n'
        '#SBATCH --ntasks='+ntasks+'\n',
        '#SBATCH --nodes='+nodes+'\n',
        '#SBATCH --cpus-per-task='+cpus+'\n',
        '#SBATCH --mem='+mem+'\n',
        '#SBATCH --mail-user='+email_address+'\n',
        '#SBATCH --mail-type=END,FAIL,TIME_LIMIT\n',
        '#SBATCH --output='+logfile+'\n',
        '#SBATCH --error=./logs/'+jobname+'_std_err.log\n',
        cmd+'\n',
        'sleep 10\n'])
    f.close()
