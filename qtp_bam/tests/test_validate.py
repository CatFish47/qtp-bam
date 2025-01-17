# -----------------------------------------------------------------------------
# Copyright (c) 2022, Qiita development team.
#
# Distributed under the terms of the Apache Software License 2.0 License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from unittest import main
from tempfile import mkdtemp
from os import remove, environ
from os.path import exists, isdir
from tempfile import mkdtemp, mkstemp
from os import remove, close
from os.path import exists, isdir, basename, splitext, join, dirname, abspath
from inspect import currentframe, getfile
from shutil import copyfile, rmtree
from json import dumps

from qiita_client import QiitaClient, ArtifactInfo
from qiita_client.testing import PluginTestCase

from qtp_bam.validate import validate


class CreateTests(PluginTestCase):
    # TODO: create
    def setUp(self):
        self.out_dir = mkdtemp()
        self._clean_up_files = [self.out_dir]
        self.source_dir = join(dirname(abspath(getfile(currentframe()))), 'test_data')
        # test file is trimmed and sorted BAM
        self.bamfile = join(self.source_dir, 'file.bam')


    def tearDown(self):
        for fp in self._clean_up_files:
            if exists(fp):
                if isdir(fp):
                    rmtree(fp)
                else:
                    remove(fp)

    def _create_job(self, artifact_type, files, command, template=1):
        """Creates a new job in Qiita so we can update its step during tests

        Parameters
        ----------
        artifact_type: str
            The artifact type
        files: dict of {str: list of str}
            The files to be validated, keyed by filepath type
        command: str (note: changed from int)
            Qiita's command id for the 'validate' operation
        template: int, optional
            The template id to which the artifact will be added

        Returns
        -------
        str, dict
            The job id and the parameters dictionary
        """
        # Create a new job
        parameters = {'template': template,
                      'files': dumps(files),
                      'artifact_type': artifact_type,
                      'analysis': None}
        data = {'command': command,
                'parameters': dumps(parameters),
                'status': 'running'}
        res = self.qclient.post('/apitest/processing_job/', data=data)
        job_id = res['job']

        return job_id, parameters

    def test_validate(self):
        # TODO: fill the following variables to create the job in the Qiita
        # test server
        test_dir = mkdtemp()
        self._clean_up_files.append(test_dir)
        copyfile(self.bamfile, f'{test_dir}/file.bam.gz')
        artifact_type = "tgz"
        files = {'tgz': [f'{test_dir}/file.bam.gz']}
        command = dumps(['BAM type', '0.0.1 - bam', 'Validate'])
        template = 1

        job_id, parameters = self._create_job(
            artifact_type, files, command, template)
        obs_success, obs_ainfo, obs_error = validate(
            self.qclient, job_id, parameters, self.out_dir)

        self.assertTrue(obs_success)
        # TODO: Fill filepaths with the expected filepath list and provide
        # the expected artifact type
        # NOTE: come back to fix
        filepaths = [(f'{test_dir}/file.bam.gz', 'tgz')]

        exp_ainfo = [ArtifactInfo(None, 'tgz', filepaths)]
        self.assertEqual(obs_ainfo, exp_ainfo)
        self.assertEqual(obs_error, "")

    # TODO: Write any other tests needed to get your coverage as close as
    # possible to 100%!!

if __name__ == '__main__':
    main()
