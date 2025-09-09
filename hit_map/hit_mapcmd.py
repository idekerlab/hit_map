#! /usr/bin/env python

import argparse
import sys
import logging
import logging.config
from cellmaps_utils import logutils
from cellmaps_utils import constants
import hit_map
from hit_map.runner import HitmapRunner

logger = logging.getLogger(__name__)


def _parse_arguments(desc, args):
    """
    Parses command line arguments

    :param desc: description to display on command line
    :type desc: str
    :param args: command line arguments usually :py:func:`sys.argv[1:]`
    :type args: list
    :return: arguments parsed by :py:mod:`argparse`
    :rtype: :py:class:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=constants.ArgParseFormatter)
    parser.add_argument('--image_meta', type=str,
                        help='image meta file with the following columns'
                             'file_directory: image direcotry'
                             'channel: blue: nucleus, green: targeted protein,red: microtubule yellow:ER'
                             'targetted_proteins: targetting protein of interest '
                             'save_prefix: save file prefix'
                        )
    parser.add_argument('--ppi_dir', type=str,
                        help='directory to the AP-MS PPI zmadex scoring file'
                             '.tsv file with header no index'
                        )
    parser.add_argument('--microscope_setup_param', type=str,
                        help='directory of the dictionary of microscope setup parameter .npy'
                             'keys including:'
                             'ni: refractive index, float'
                             ' NA: numerical aperture,float'
                             'lambda: wavelength, dictionary {blue:int, red:int, green: int, yellow: int}'
                             'resxy: pixel size, int'
                             'resz: destance between panels,int'
                             'threads: for multiprocessing,int')
    parser.add_argument('--psigma', type=float,
                        help='psigma parameter for deconwolf')
    parser.add_argument('--provenance_img',
                        help='Path to file containing provenance of image '
                             'information about input files in JSON format. '
                             'This is required if inputdir does not contain '
                             'ro-crate-metadata.json file.')
    parser.add_argument('--provenance_ppi',
                        help='Path to file containing provenance of AP-MS '
                             'information about input files in JSON format. '
                             'This is required if inputdir does not contain '
                             'ro-crate-metadata.json file.')
    parser.add_argument("--generate_hierarchy", action="store_true", default=False,
                        help='Generate hierarchy from co-embedding of the image/AP-MS. '
                             'Default is False. Use this flag to enable hierarchy generation.'
                        )
    parser.add_argument('--outdir',
                        help='Directory to write results to')
    parser.add_argument('--logconf', default=None,
                        help='Path to python logging configuration file in '
                             'this format: https://docs.python.org/3/library/'
                             'logging.config.html#logging-config-fileformat '
                             'Setting this overrides -v parameter which uses '
                             ' default logger. (default None)')
    parser.add_argument('--exitcode', help='Exit code this command will return',
                        default=0, type=int)
    parser.add_argument('--skip_logging', action='store_true',
                        help='If set, output.log, error.log '
                             'files will not be created')
    parser.add_argument('--provenance',
                        help='Path to file containing provenance '
                             'information about input files in JSON format. '
                             'This is required and not including will output '
                             'and error message with example of file')
    parser.add_argument('--verbose', '-v', action='count', default=1,
                        help='Increases verbosity of logger to standard '
                             'error for log messages in this module. Messages are '
                             'output at these python logging levels '
                             '-v = WARNING, -vv = INFO, '
                             '-vvv = DEBUG, -vvvv = NOTSET (default ERROR '
                             'logging)')
    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' +
                                 hit_map.__version__))

    return parser.parse_args(args)


def main(args):
    """
    Main entry point for program

    :param args: arguments passed to command line usually :py:func:`sys.argv[1:]`
    :type args: list

    :return: return value of :py:meth:`hit_map.runner.HitmapRunner.run`
             or ``2`` if an exception is raised
    :rtype: int
    """
    desc = """
    Version {version}

    Invokes run() method on HitmapRunner

    """.format(version=hit_map.__version__)
    theargs = _parse_arguments(desc, args[1:])
    theargs.program = args[0]
    theargs.version = hit_map.__version__

    try:
        logutils.setup_cmd_logging(theargs)
        return HitmapRunner(image_meta=theargs.image_meta,
                            ppi_dir=theargs.ppi_dir,
                            microscope_setup_param=theargs.microscope_setup_param,
                            psigma=theargs.psigma,
                            provenance_img=theargs.provenance_img,
                            provenance_ppi=theargs.provenance_ppi,
                            generate_hierarchy=theargs.generate_hierarchy,
                            outdir=theargs.outdir,
                            exitcode=theargs.exitcode,
                            skip_logging=theargs.skip_logging,
                            input_data_dict=theargs.__dict__).run()

    except Exception as e:
        logger.exception('Caught exception: ' + str(e))
        return 2
    finally:
        logging.shutdown()


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
