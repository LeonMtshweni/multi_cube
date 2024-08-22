# this function writes the slurm/bash script 
def write_slurm(bash_filename,
                jobname,
                logfile,
                cmd,
                email_address,
                time,  
                partition,
                ntasks,
                nodes,
                cpus,
                mem):

    f = open(bash_filename,'w')

    f.writelines([
        '#!/bin/bash\n',
        f'#file: {bash_filename}:\n',
        f'#SBATCH --job-name={jobname}\n',
        f'#SBATCH --time={time}\n',
        f'#SBATCH --partition={partition}\n',
        f'#SBATCH --ntasks={ntasks}\n',
        f'#SBATCH --nodes={nodes}\n',
        f'#SBATCH --cpus-per-task={cpus}\n',
        f'#SBATCH --mem={mem}\n',
        f'#SBATCH --mail-user={email_address}\n',
        f'#SBATCH --mail-type=END,FAIL,TIME_LIMIT\n',
        f'#SBATCH --output={logfile}\n',
        f'#SBATCH --error=./logs/{jobname}_std_err.log\n',
        f'{cmd}\n',
        'sleep 10\n'
    ])

    f.close()
