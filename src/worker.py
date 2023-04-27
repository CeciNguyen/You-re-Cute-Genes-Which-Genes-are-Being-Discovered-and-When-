from jobs import qw, wd, update_job_status

@qw.worker
def execute_job(jid):
     # update the job status to in progress
    update_job_status(jid, 'in progress')

    # get job parameters
    job_params = rd.hgetall(jid)
    start = job_params['start']
    end = job_params['end']

    for item in rd.keys():
        gene = json.loads(rd.get(item))
        year = gene['date_approved_reserved'][0:4]
        years.append(year)
    yeard = dict(Counter(years))
    yeard = dict(sorted(yeard.items()))
    y = []
    c = []
    for item in yeard:
        y.append(item)
        c.append(yeard[item])
    sind = y.index(str(start))
    eind = y.index(str(end))+1
    y = y[sind:eind]
    c = c[sind:eind]
    plt.figure(figsize=(28,6))
    plt.bar(y, c, width = 0.35)
    plt.xlabel("Years")
    plt.ylabel("Number of Entries Approved")
    plt.title("Genes Approved Each Year")
    plt.savefig('approvalyears.png')
    file_bytes = open('./approvalyears.png', 'rb').read()
    dset = {}
    for x in range(len(y)):
        dset.update({str(y[x]):x[x]})
    
    # save the image back on the redis database
    wd.set("{jid}_plot", file_bytes)
    # update job status to complete
    update_job_status(jid, 'complete')


execute_job()

