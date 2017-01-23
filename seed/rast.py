import attr
import requests
import yaml

from . import perlyaml

formats = {
    'genbank': '.gbk',
    'genbank_stripped': '.ec-stripped.gbk',
    'embl': '.embl',
    'embl_stripped': '.ec-stripped.embl',
    'gff3': '.gff',
    'gff3_stripped': '.ec-stripped.gff',
    'gtf': '.gtf',
    'gtf_stripped': '.ec-stripped.gtf',
    'rast_tarball': '.tgz',
    'nucleic_acid': '.fna',
    'amino_acid': '.faa',
    'table_txt': '.txt',
    'table_xls': '.xls',
}


def _member(*items):
    def f(_i, _a, v):
        assert v in items

    return f


@attr.s
class Job(object):
    file = attr.ib()
    filetype = attr.ib('fasta', validator=_member('fasta', 'genbank'))
    taxonomyID = attr.ib(None)
    geneticCode = attr.ib(None)  # if Fasta and not TaxonomyID, geneticCode => [1 | 4 | 11]
    domain = attr.ib(None)  # 'Bacteria Archaea Viruses', 'Eukaryota'
    organismName = attr.ib(None)
    keepGeneCalls = attr.ib(False, convert=int)
    geneCaller = attr.ib('rast', validator=_member('rast', 'glimmer3'))
    nonActive = attr.ib(None)
    determineFamily = attr.ib(None)
    kmerDataset = attr.ib(None)
    fixFrameshifts = attr.ib(None)
    backfillGaps = attr.ib(None)
    annotationScheme = attr.ib(None)

    def params(self):
        params = {}
        for k, v in attr.asdict(self).items():
            if v is not None:
                if k == 'file':
                    with open(v) as f:
                        v = f.read()
                params['-' + k] = v
        return params


def _wrap(jobs):
    unwrap = lambda v: v
    if isinstance(jobs, int):
        jobs = [jobs]
        unwrap = lambda v: v[jobs[0]]
    return unwrap, jobs


class RAST(object):
    def __init__(
        self,
        username,
        password,
        endpoint='http://servers.nmpdr.org/rast/server.cgi'
    ):
        self._username = username
        self._password = password
        self._endpoint = endpoint

        self._session = requests.Session()

    def status(self, jobs):
        q = 'status_of_RAST_job'
        return self._query_jobs(q, jobs)

    def kill(self, jobs):
        q = 'kill_RAST_job'
        return self._query_jobs(q, jobs)

    def delete(self, jobs):
        q = 'delete_RAST_job'
        return self._query_jobs(q, jobs)

    def metadata(self, job):
        q = 'get_job_metadata'
        return self._query(q, {'-job': job})

    def retrieve(self, job, format):
        q = 'retrieve_RAST_job'
        args = {'-job': job, '-format': format}
        if format not in formats:
            err = '{!r} is not in {}'.format(format, formats.keys())
            raise ValueError(err)
        return self._query(q, args, decode_yaml=False)

    def submit(self, job):
        q = 'submit_RAST_job'
        return self._query(q, job.params())

    def copy(self, src, dst):
        raise NotImplementedError

    def _query(self, function, params, decode_yaml=True):
        form = dict(
            username=self._username,
            password=self._password,
            function=function,
            args=perlyaml.dumps(params),
        )
        resp = self._session.post(self._endpoint, data=form)
        if decode_yaml:
            return yaml.safe_load(resp.text)
        return resp.text

    def _query_jobs(self, function, jobs):
        unwrap, jobs = _wrap(jobs)
        return unwrap(self._query(function, {'-job': jobs}))
