import momapy.io.core
import momapy.sbgn.io.sbgnml
import momapy.sbgn.io.pickle

momapy.io.core.register_reader("sbgnml-0.2", momapy.sbgn.io.sbgnml.SBGNML0_2Reader)
momapy.io.core.register_reader("sbgnml-0.3", momapy.sbgn.io.sbgnml.SBGNML0_3Reader)
momapy.io.core.register_reader("sbgnml", momapy.sbgn.io.sbgnml.SBGNML0_3Reader)
momapy.io.core.register_writer("sbgnml-0.3", momapy.sbgn.io.sbgnml.SBGNML0_3Writer)
momapy.io.core.register_writer("sbgnml", momapy.sbgn.io.sbgnml.SBGNML0_3Writer)
momapy.io.core.register_reader("sbgn-pickle", momapy.sbgn.io.pickle.SBGNPickleReader)
momapy.io.core.register_writer("sbgn-pickle", momapy.sbgn.io.pickle.SBGNPickleWriter)
