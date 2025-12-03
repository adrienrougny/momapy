from pathlib import Path
from momapy.sbml.io import sbml
from momapy.sbml import core


model_path = Path("../models/e_coli_core.xml")
#model_path = Path("../models/matched_annotated_repressilator_BIOMD0000000012.xml")

result = sbml.SBMLReader.read(model_path)
#print(result)

model = result.obj
#print(model)


annotations_map = result.annotations
#print(annotations_map)


print('------------------- General ------------------')
print("Model ID:", model.id_)
print("Name:", model.name) # need to check this field
print("Compartments:", len(model.compartments))
print("Species:", len(model.species))
print("Reactions:", len(model.reactions))
print("Genes:", len(model.genes))
print("Has objective:", model.objective is not None)


print()



print('------------------ Compartments ----------------')
one_comp = next(iter(model.compartments), None)

if one_comp is None:
    print("⚠ No compartments in this model.")
else:
    print("Compartment ID:", one_comp.id_)
    print("Name:", one_comp.name)
    print("SBO term:", one_comp.sbo_term)
    print("Metaid:", one_comp.metaid)
    print("Outside compartment:", one_comp.outside)


print()

print('------------------ Species/Reactions ----------------')
one_species = next(iter(model.species), None)

if one_species is None:
    print("⚠ No species in this model.")
else:
    print("Species ID:", one_species.id_)
    print("Name:", one_species.name)
    print("Compartment:", one_species.compartment.id_ if one_species.compartment else None)
    print("SBO:", one_species.sbo_term)
    print("Metaid:", one_species.metaid)


print()

print('------------------ Reactions Bounds----------------')
one_rx = next(iter(model.reactions), None)

if one_rx is None:
    print("⚠ No reactions in this model.")
else:
    print("Reaction ID:", one_rx.id_)
    print("Name:", one_rx.name)
    print("Reversible:", one_rx.reversible)
    print("SBO term:", one_rx.sbo_term)
    print("Lower bound:", one_rx.lower_flux_bound)
    print("Upper bound:", one_rx.upper_flux_bound)

print()


print('------------------ Reactions stoichiometry ----------------')
def reaction_to_string(r: core.Reaction):
    def side(refs):
        if not refs:
            return "(none)"
        out = []
        for sr in refs:
            coeff = sr.stoichiometry if sr.stoichiometry is not None else 1.0
            out.append(f"{coeff:g} {sr.referred_species.id_}")
        return " + ".join(out)

    arrow = "<->" if r.reversible else "-->"
    return f"{side(r.reactants)}  {arrow}  {side(r.products)}"

if one_rx:
    print("Reaction:", one_rx.id_)
    print(reaction_to_string(one_rx))

print()

print('------------------ Reactions gpr ----------------')
if one_rx:
    print("Reaction:", one_rx.id_)
    print("GPR:", one_rx.safe_gpr_string())   # always safe


print()


print('------------------ Genes (for GEMs) ----------------')
one_gene = next(iter(model.genes), None)

if one_gene is None:
    print("⚠ No genes in this model (Non-GEM model).")
else:
    print("GeneProduct ID:", one_gene.id_)
    print("Name:", one_gene.name)
    print("Label:", one_gene.label)
    print("SBO:", one_gene.sbo_term)
    print("Metaid:", one_gene.metaid)


print('------------------ Genes gpr ----------------')
try:
    rxs = one_gene.associated_reactions(model)
    for rx in rxs:
        print(rx.id_, "|", rx.name)

except:
    print("⚠ No genes in this model (Non-GEM model).")

print()


print('------------------ Model Objective ----------------')
print("Objective ID:", model.safe_objective_id())
print("Objective type:", model.safe_objective_type())

one_flux_obj = None
fos = model.safe_flux_objectives() # Need to check also this method
if fos:
    one_flux_obj = fos

if one_flux_obj is None:
    print("⚠ No flux objectives in this model.")
else:
    print("FluxObjective reaction:", one_flux_obj.reaction_id)
    print("Coefficient:", one_flux_obj.coefficient)
    print("Linked Reaction Object:", one_flux_obj.reaction)

print()
