import momapy.io.core
import momapy.sbgn.io.sbgnml
import momapy.sbgn.io.pickle
import momapy.celldesigner.io.celldesigner
import momapy.celldesigner.io.pickle
import momapy.sbml.io.sbml

momapy.io.core.register_reader("sbgnml-0.2", momapy.sbgn.io.sbgnml.SBGNML0_2Reader)
momapy.io.core.register_reader("sbgnml-0.3", momapy.sbgn.io.sbgnml.SBGNML0_3Reader)
momapy.io.core.register_reader("sbgnml", momapy.sbgn.io.sbgnml.SBGNML0_3Reader)
momapy.io.core.register_writer("sbgnml-0.3", momapy.sbgn.io.sbgnml.SBGNML0_3Writer)
momapy.io.core.register_writer("sbgnml", momapy.sbgn.io.sbgnml.SBGNML0_3Writer)

momapy.io.core.register_reader("sbgn-pickle", momapy.sbgn.io.pickle.SBGNPickleReader)
momapy.io.core.register_writer("sbgn-pickle", momapy.sbgn.io.pickle.SBGNPickleWriter)

momapy.io.core.register_reader(
    "celldesigner", momapy.celldesigner.io.celldesigner.CellDesignerReader
)

momapy.io.core.register_reader(
    "celldesigner_pickle", momapy.celldesigner.io.pickle.CellDesignerPickleReader
)
momapy.io.core.register_writer(
    "celldesigner_pickle", momapy.celldesigner.io.pickle.CellDesignerPickleWriter
)


momapy.io.core.register_reader("sbml", momapy.sbml.io.sbml.SBMLReader)
