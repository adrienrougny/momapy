import os
import collections

import frozendict
import lxml.objectify
import lxml.etree

import momapy.core
import momapy.geometry
import momapy.positioning
import momapy.io
import momapy.coloring
import momapy.sbml.core
import momapy.utils
import momapy.builder


class SBMLReader(momapy.io.Reader):
    _CD_NAMESPACE = "http://www.sbml.org/2001/ns/celldesigner"
    _RDF_NAMESPACE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    _MATH_NAMESPACE = "http://www.w3.org/1998/Math/MathML"

    _QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER = {
        ("http://biomodels.net/biology-qualifiers/", "encodes"): momapy.sbml.core.BQBiol.ENCODES,
        ("http://biomodels.net/biology-qualifiers/", "hasPart"): momapy.sbml.core.BQBiol.HAS_PART,
        ("http://biomodels.net/biology-qualifiers/", "hasProperty"): momapy.sbml.core.BQBiol.HAS_PROPERTY,
        ("http://biomodels.net/biology-qualifiers/", "hasVersion"): momapy.sbml.core.BQBiol.HAS_VERSION,
        ("http://biomodels.net/biology-qualifiers/", "is"): momapy.sbml.core.BQBiol.IS,
        ("http://biomodels.net/biology-qualifiers/", "isDescribedBy"): momapy.sbml.core.BQBiol.IS_DESCRIBED_BY,
        ("http://biomodels.net/biology-qualifiers/", "isEncodedBy"): momapy.sbml.core.BQBiol.IS_ENCODED_BY,
        ("http://biomodels.net/biology-qualifiers/", "isHomologTo"): momapy.sbml.core.BQBiol.IS_HOMOLOG_TO,
        ("http://biomodels.net/biology-qualifiers/", "isPartOf"): momapy.sbml.core.BQBiol.IS_PART_OF,
        ("http://biomodels.net/biology-qualifiers/", "isPropertyOf"): momapy.sbml.core.BQBiol.IS_PROPERTY_OF,
        ("http://biomodels.net/biology-qualifiers/", "isVersionOf"): momapy.sbml.core.BQBiol.IS_VERSION_OF,
        ("http://biomodels.net/biology-qualifiers/", "occursIn"): momapy.sbml.core.BQBiol.OCCURS_IN,
        ("http://biomodels.net/biology-qualifiers/", "hasTaxon"): momapy.sbml.core.BQBiol.HAS_TAXON,
        ("http://biomodels.net/biology-qualifiers/", "hasInstance"): momapy.sbml.core.BQModel.HAS_INSTANCE,
        ("http://biomodels.net/model-qualifiers/", "is"): momapy.sbml.core.BQModel.IS,
        ("http://biomodels.net/model-qualifiers/", "isDerivedFrom"): momapy.sbml.core.BQModel.IS_DERIVED_FROM,
        ("http://biomodels.net/model-qualifiers/", "isDescribedBy"): momapy.sbml.core.BQModel.IS_DESCRIBED_BY,
        ("http://biomodels.net/model-qualifiers/", "isInstanceOf"): momapy.sbml.core.BQModel.IS_INSTANCE_OF,
    }



    @classmethod
    def check_file(cls, file_path: str | os.PathLike):
        try:
            with open(file_path) as f:
                for line in f:
                    if "<sbml" in line:
                        return True
        except Exception:
            pass
        return False

    @classmethod
    def read(
        cls,
        file_path: str | os.PathLike,
        with_annotations: bool = True,
        with_notes: bool = True,
    ) -> momapy.io.ReaderResult:
        try:
            sbml_document = lxml.objectify.parse(file_path)
        except Exception as e:
            raise ValueError(f"Failed to parse SBML: {file_path}") from e

        root = sbml_document.getroot()

        if not hasattr(root, "model"):
            empty = momapy.sbml.core.SBMLModel()
            return momapy.io.ReaderResult(
                obj=empty,
                notes=frozendict.frozendict(),
                annotations=frozendict.frozendict(),
                file_path=file_path,
                ids=frozendict.frozendict(),
            )

        model_obj, annotations, notes, ids = cls._make_main_obj_from_sbml_model(
            sbml_model=root.model,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )

        return momapy.io.ReaderResult(
            obj=model_obj,
            notes=notes,
            annotations=annotations,
            file_path=file_path,
            ids=ids,
        )

    # ----------------------------------------------------------------------
    # Basic helpers
    # ----------------------------------------------------------------------

    @classmethod
    def _get_prefix_and_name_from_tag(cls, tag: str):
        prefix, name = tag.split("}")
        return prefix[1:], name

    @classmethod
    def _get_compartments(cls, sbml_model):
        lst = getattr(sbml_model, "listOfCompartments", None)
        return [] if lst is None else list(getattr(lst, "compartment", []))

    @classmethod
    def _get_species(cls, sbml_model):
        lst = getattr(sbml_model, "listOfSpecies", None)
        return [] if lst is None else list(getattr(lst, "species", []))

    @classmethod
    def _get_reactions(cls, sbml_model):
        lst = getattr(sbml_model, "listOfReactions", None)
        return [] if lst is None else list(getattr(lst, "reaction", []))

    @classmethod
    def _get_reactants(cls, sbml_reaction):
        lst = getattr(sbml_reaction, "listOfReactants", None)
        return [] if lst is None else list(getattr(lst, "speciesReference", []))

    @classmethod
    def _get_products(cls, sbml_reaction):
        lst = getattr(sbml_reaction, "listOfProducts", None)
        return [] if lst is None else list(getattr(lst, "speciesReference", []))

    @classmethod
    def _get_modifiers(cls, sbml_reaction):
        lst = getattr(sbml_reaction, "listOfModifiers", None)
        return [] if lst is None else list(getattr(lst, "modifierSpeciesReference", []))

    @classmethod
    def _get_notes_from_sbml_element(cls, el):
        return getattr(el, "notes", None)

    @classmethod
    def _get_annotation_from_sbml_element(cls, el):
        return getattr(el, "annotation", None)

    @classmethod
    def _get_rdf_from_sbml_element(cls, el):
        ann = cls._get_annotation_from_sbml_element(el)
        if ann is None:
            return None
        return getattr(ann, f"{{{cls._RDF_NAMESPACE}}}RDF", None)

    @classmethod
    def _make_notes_from_sbml_element(cls, el):
        notes = cls._get_notes_from_sbml_element(el)
        if notes is None:
            return []
        for child in notes.iterchildren():
            return lxml.etree.tostring(child)
        return None

    @classmethod
    def _make_annotations_from_sbml_element(cls, el):
        rdf = cls._get_rdf_from_sbml_element(el)
        if rdf is None:
            return []

        desc = getattr(rdf, "Description", None)
        if desc is None:
            return []

        annots = []
        for bq_element in desc.getchildren():
            prefix, name = cls._get_prefix_and_name_from_tag(bq_element.tag)
            qualifier = cls._QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER.get((prefix, name))
            if qualifier is None:
                continue

            bags = getattr(bq_element, f"{{{cls._RDF_NAMESPACE}}}Bag", [])
            for bag in bags:
                lis = getattr(bag, "li", [])
                resources = [
                    li.get(f"{{{cls._RDF_NAMESPACE}}}resource") for li in lis
                ]
                annots.append(
                    momapy.sbml.core.RDFAnnotation(
                        qualifier=qualifier,
                        resources=frozenset(resources),
                    )
                )
        return annots



    @classmethod
    def _get_parameters(cls, sbml_model):
        lst = getattr(sbml_model, "listOfParameters", None)
        return [] if lst is None else list(getattr(lst, "parameter", []))

    @classmethod
    def _make_param_id_to_value_map(cls, sbml_model):
        mapping = {}
        for p in cls._get_parameters(sbml_model):
            pid = p.get("id")
            val = p.get("value")
            if pid is not None and val is not None:
                try:
                    mapping[pid] = float(val)
                except ValueError:
                    pass
        return mapping

    # ----------------------------------------------------------------------
    #  Main builder
    # ----------------------------------------------------------------------

    @classmethod
    def _make_model_no_subelements(cls):
        builder = momapy.sbml.core.SBMLModelBuilder()
        if getattr(builder, "id_", None) is None:
            builder.id_ = "sbml_model"
        return builder

    @classmethod
    def _make_main_obj_from_sbml_model(
        cls,
        sbml_model,
        with_annotations: bool = True,
        with_notes: bool = True,
    ):
        model = cls._make_model_no_subelements()

        sbml_id_to_model_element: dict[str, momapy.core.ModelElement] = {}
        map_element_to_annotations = collections.defaultdict(set)
        map_element_to_notes = collections.defaultdict(set)
        map_element_to_ids = collections.defaultdict(set)

        param_map = cls._make_param_id_to_value_map(sbml_model)

        # 1. compartments
        cls._read_compartments(
            sbml_model,
            model,
            sbml_id_to_model_element,
            map_element_to_annotations,
            map_element_to_notes,
            map_element_to_ids,
            with_annotations,
            with_notes,
        )

        # 2. species
        cls._read_species(
            sbml_model,
            model,
            sbml_id_to_model_element,
            map_element_to_annotations,
            map_element_to_notes,
            map_element_to_ids,
            with_annotations,
            with_notes,
        )

        # 3. genes
        cls._read_genes(
            sbml_model,
            model,
            sbml_id_to_model_element,
            map_element_to_annotations,
            map_element_to_notes,
            map_element_to_ids,
            with_annotations,
            with_notes,
        )

        # 4. reactions
        cls._read_reactions(
            sbml_model,
            model,
            sbml_id_to_model_element,
            map_element_to_annotations,
            map_element_to_notes,
            map_element_to_ids,
            param_map,
            with_annotations,
            with_notes,
        )

        # 5. objective (single)
        cls._read_objective(
            sbml_model,
            model,
            sbml_id_to_model_element,
            map_element_to_annotations,
            map_element_to_notes,
            map_element_to_ids,
            with_annotations,
            with_notes,
        )

        final_obj = momapy.builder.object_from_builder(model)

        if with_annotations:
            anns = cls._make_annotations_from_sbml_element(sbml_model)
            if anns:
                map_element_to_annotations[final_obj].update(anns)
        if with_notes:
            nts = cls._make_notes_from_sbml_element(sbml_model)
            if nts:
                map_element_to_notes[final_obj].add(nts)

        ann_frozen = frozendict.frozendict(
            {k: frozenset(v) for k, v in map_element_to_annotations.items()}
        )
        notes_frozen = frozendict.frozendict(
            {k: frozenset(v) for k, v in map_element_to_notes.items()}
        )
        ids_frozen = frozendict.frozendict(
            {k: frozenset(v) for k, v in map_element_to_ids.items()}
        )

        return final_obj, ann_frozen, notes_frozen, ids_frozen

    # ----------------------------------------------------------------------
    # Compartments
    # ----------------------------------------------------------------------

    @classmethod
    def _read_compartments(
        cls,
        sbml_model,
        model,
        sbml_id_map,
        map_ann,
        map_notes,
        map_ids,
        wa,
        wn,
    ):
        for comp in cls._get_compartments(sbml_model):
            m = model.new_element(momapy.sbml.core.Compartment)
            m.id_ = comp.get("id")
            m.name = comp.get("name")
            m.metaid = comp.get("metaid")
            m.sbo_term = comp.get("sboTerm")

            m = momapy.builder.object_from_builder(m)
            m = momapy.utils.add_or_replace_element_in_set(
                m, model.compartments, func=lambda a, b: a.id_ < b.id_
            )

            sbml_id_map[m.id_] = m
            map_ids[m].add(m.id_)

            if wa:
                anns = cls._make_annotations_from_sbml_element(comp)
                if anns:
                    map_ann[m].update(anns)
            if wn:
                nts = cls._make_notes_from_sbml_element(comp)
                if nts:
                    map_notes[m].add(nts)

    # ----------------------------------------------------------------------
    # Species
    # ----------------------------------------------------------------------

    @classmethod
    def _read_species(
        cls,
        sbml_model,
        model,
        sbml_id_map,
        map_ann,
        map_notes,
        map_ids,
        wa,
        wn,
    ):
        for sp in cls._get_species(sbml_model):
            m = model.new_element(momapy.sbml.core.Species)
            m.id_ = sp.get("id")
            m.name = sp.get("name")
            m.metaid = sp.get("metaid")
            m.sbo_term = sp.get("sboTerm")

            comp_id = sp.get("compartment")
            if comp_id and comp_id in sbml_id_map:
                m.compartment = sbml_id_map[comp_id]

            m = momapy.builder.object_from_builder(m)
            m = momapy.utils.add_or_replace_element_in_set(
                m, model.species, func=lambda a, b: a.id_ < b.id_
            )

            sbml_id_map[m.id_] = m
            map_ids[m].add(m.id_)

            if wa:
                anns = cls._make_annotations_from_sbml_element(sp)
                if anns:
                    map_ann[m].update(anns)
            if wn:
                nts = cls._make_notes_from_sbml_element(sp)
                if nts:
                    map_notes[m].add(nts)

    # ----------------------------------------------------------------------
    # Genes / GeneProducts
    # ----------------------------------------------------------------------

    @classmethod
    def _read_genes(
        cls,
        sbml_model,
        model,
        sbml_id_map,
        map_ann,
        map_notes,
        map_ids,
        wa,
        wn,
    ):
        # Support FBC v1, v2, v3
        FBC_v1 = "{http://www.sbml.org/sbml/level3/version1/fbc/version1}"
        FBC_v2 = "{http://www.sbml.org/sbml/level3/version1/fbc/version2}"
        FBC_v3 = "{http://www.sbml.org/sbml/level3/version1/fbc/version3}"

        for FBC in (FBC_v1, FBC_v2, FBC_v3):
            list_gp = getattr(sbml_model, f"{FBC}listOfGeneProducts", None)
            if list_gp is None:
                continue

            for gp in getattr(list_gp, f"{FBC}geneProduct", []):
                m = model.new_element(momapy.sbml.core.GeneProduct)
                m.id_ = gp.get(f"{FBC}id") or gp.get("id")
                m.label = gp.get(f"{FBC}label") or gp.get("label")
                m.name = gp.get(f"{FBC}name") or gp.get("name")
                m.metaid = gp.get("metaid")

                m = momapy.builder.object_from_builder(m)
                model.genes.add(m)
                sbml_id_map[m.id_] = m
                map_ids[m].add(m.id_)

                if wa:
                    annotation_elem = None
                    for ch in gp.iterchildren():
                        if ch.tag.endswith("annotation"):
                            annotation_elem = ch
                            break
                    if annotation_elem is not None:
                        anns = cls._make_annotations_from_sbml_element(annotation_elem)
                        if anns:
                            map_ann[m].update(anns)

                if wn:
                    nts = cls._make_notes_from_sbml_element(gp)
                    if nts:
                        map_notes[m].add(nts)

    # ----------------------------------------------------------------------
    # GPR parsing
    # ----------------------------------------------------------------------

    @classmethod
    def _parse_gpr_node(cls, node, sbml_id_map):
        if node is None:
            return None

        tag = node.tag.split("}")[-1]

        if tag in ("and", "or"):
            children = []
            for ch in node.getchildren():
                parsed = cls._parse_gpr_node(ch, sbml_id_map)
                if parsed:
                    children.append(parsed)
            return momapy.sbml.core.GeneProductAssociation(
                operator=tag,
                children=tuple(children),
            )

        if tag == "geneProductRef":
            gid = (
                node.get("geneProduct")
                or node.get("{http://www.sbml.org/sbml/level3/version1/fbc/version1}geneProduct")
                or node.get("{http://www.sbml.org/sbml/level3/version1/fbc/version2}geneProduct")
                or node.get("{http://www.sbml.org/sbml/level3/version1/fbc/version3}geneProduct")
            )
            gene = sbml_id_map.get(gid)
            if gene is None:
                return None
            return momapy.sbml.core.GeneProductRef(gene_product=gene)

        return None

    @classmethod
    def _parse_gpr(cls, sbml_reaction, sbml_id_map):
        FBC_v1 = "{http://www.sbml.org/sbml/level3/version1/fbc/version1}"
        FBC_v2 = "{http://www.sbml.org/sbml/level3/version1/fbc/version2}"
        FBC_v3 = "{http://www.sbml.org/sbml/level3/version1/fbc/version3}"

        assoc = (
            getattr(sbml_reaction, f"{FBC_v1}geneProductAssociation", None)
            or getattr(sbml_reaction, f"{FBC_v2}geneProductAssociation", None)
            or getattr(sbml_reaction, f"{FBC_v3}geneProductAssociation", None)
        )
        if assoc is None:
            return None

        kids = assoc.getchildren()
        if not kids:
            return None

        return cls._parse_gpr_node(kids[0], sbml_id_map)

    # ----------------------------------------------------------------------
    # Reactions
    # ----------------------------------------------------------------------

    @classmethod
    def _resolve_bound(cls, raw, param_map):
        if raw is None:
            return None
        try:
            return float(raw)
        except Exception:
            return param_map.get(raw, None)

    @classmethod
    def _read_reactions(
        cls,
        sbml_model,
        model,
        sbml_id_map,
        map_ann,
        map_notes,
        map_ids,
        param_map,
        wa,
        wn,
    ):
        FBC_v1 = "{http://www.sbml.org/sbml/level3/version1/fbc/version1}"
        FBC_v2 = "{http://www.sbml.org/sbml/level3/version1/fbc/version2}"
        FBC_v3 = "{http://www.sbml.org/sbml/level3/version1/fbc/version3}"

        for rx in cls._get_reactions(sbml_model):
            m = model.new_element(momapy.sbml.core.Reaction)
            m.id_ = rx.get("id")
            m.name = rx.get("name")
            m.metaid = rx.get("metaid")
            m.sbo_term = rx.get("sboTerm")
            m.reversible = rx.get("reversible") == "true"

            lb_raw = (
                rx.get(f"{FBC_v3}lowerFluxBound")
                or rx.get(f"{FBC_v2}lowerFluxBound")
                or rx.get(f"{FBC_v1}lowerFluxBound")
                or rx.get("lowerFluxBound")
            )
            ub_raw = (
                rx.get(f"{FBC_v3}upperFluxBound")
                or rx.get(f"{FBC_v2}upperFluxBound")
                or rx.get(f"{FBC_v1}upperFluxBound")
                or rx.get("upperFluxBound")
            )

            m.lower_flux_bound = cls._resolve_bound(lb_raw, param_map)
            m.upper_flux_bound = cls._resolve_bound(ub_raw, param_map)

            # reactants
            for sr in cls._get_reactants(rx):
                sid = sr.get("species")
                sr_m = model.new_element(momapy.sbml.core.SpeciesReference)
                sr_m.id_ = sr.get("metaid") or f"{m.id_}_{sid}_reactant"
                st = sr.get("stoichiometry")
                if st is not None:
                    try:
                        sr_m.stoichiometry = float(st)
                    except Exception:
                        pass
                sr_m.referred_species = sbml_id_map.get(sid)
                sr_m = momapy.builder.object_from_builder(sr_m)
                m.reactants.add(sr_m)
                sbml_id_map[sr_m.id_] = sr_m

            # products
            for sr in cls._get_products(rx):
                sid = sr.get("species")
                sr_m = model.new_element(momapy.sbml.core.SpeciesReference)
                sr_m.id_ = sr.get("metaid") or f"{m.id_}_{sid}_product"
                st = sr.get("stoichiometry")
                if st is not None:
                    try:
                        sr_m.stoichiometry = float(st)
                    except Exception:
                        pass
                sr_m.referred_species = sbml_id_map.get(sid)
                sr_m = momapy.builder.object_from_builder(sr_m)
                m.products.add(sr_m)
                sbml_id_map[sr_m.id_] = sr_m

            # modifiers
            for sr in cls._get_modifiers(rx):
                sid = sr.get("species")
                sr_m = model.new_element(momapy.sbml.core.ModifierSpeciesReference)
                sr_m.id_ = sr.get("metaid") or f"{m.id_}_{sid}_modifier"
                sr_m.referred_species = sbml_id_map.get(sid)
                sr_m = momapy.builder.object_from_builder(sr_m)
                m.modifiers.add(sr_m)
                sbml_id_map[sr_m.id_] = sr_m

            # GPR
            gpr = cls._parse_gpr(rx, sbml_id_map)
            if gpr is not None:
                m.gene_association = gpr

            kl = model.new_element(momapy.sbml.core.KineticLaw)
            kl = momapy.builder.object_from_builder(kl)
            m.kinetic_law = kl

            m = momapy.builder.object_from_builder(m)
            m = momapy.utils.add_or_replace_element_in_set(
                m, model.reactions, func=lambda a, b: a.id_ < b.id_
            )

            sbml_id_map[m.id_] = m
            map_ids[m].add(m.id_)

            if wa:
                anns = cls._make_annotations_from_sbml_element(rx)
                if anns:
                    map_ann[m].update(anns)
            if wn:
                nts = cls._make_notes_from_sbml_element(rx)
                if nts:
                    map_notes[m].add(nts)

    # ----------------------------------------------------------------------
    # Objective
    # ----------------------------------------------------------------------

    @classmethod
    def _read_objective(
        cls,
        sbml_model,
        model,
        sbml_id_map,
        map_ann,
        map_notes,
        map_ids,
        wa,
        wn,
    ):
        # Support FBC v1, v2, v3
        FBC_v1 = "{http://www.sbml.org/sbml/level3/version1/fbc/version1}"
        FBC_v2 = "{http://www.sbml.org/sbml/level3/version1/fbc/version2}"
        FBC_v3 = "{http://www.sbml.org/sbml/level3/version1/fbc/version3}"

        list_obj = (
            getattr(sbml_model, f"{FBC_v3}listOfObjectives", None)
            or getattr(sbml_model, f"{FBC_v2}listOfObjectives", None)
            or getattr(sbml_model, f"{FBC_v1}listOfObjectives", None)
        )

        if list_obj is None:
            model.objective = None
            return

        active_id = (
            list_obj.get(f"{FBC_v3}activeObjective")
            or list_obj.get(f"{FBC_v2}activeObjective")
            or list_obj.get(f"{FBC_v1}activeObjective")
            or list_obj.get("activeObjective")
        )

        objs = (
            getattr(list_obj, f"{FBC_v3}objective", None)
            or getattr(list_obj, f"{FBC_v2}objective", None)
            or getattr(list_obj, f"{FBC_v1}objective", None)
        )
        if objs is None:
            model.objective = None
            return

        for sbml_obj in objs:
            obj_id = (
                sbml_obj.get(f"{FBC_v3}id")
                or sbml_obj.get(f"{FBC_v2}id")
                or sbml_obj.get(f"{FBC_v1}id")
                or sbml_obj.get("id")
            )
            obj_type = (
                sbml_obj.get(f"{FBC_v3}type")
                or sbml_obj.get(f"{FBC_v2}type")
                or sbml_obj.get(f"{FBC_v1}type")
                or sbml_obj.get("type")
                or "maximize"
            )

            # flux objectives
            flux_objs: list[momapy.sbml.core.FluxObjective] = []

            list_flux = (
                getattr(sbml_obj, f"{FBC_v3}listOfFluxObjectives", None)
                or getattr(sbml_obj, f"{FBC_v2}listOfFluxObjectives", None)
                or getattr(sbml_obj, f"{FBC_v1}listOfFluxObjectives", None)
            )

            if list_flux is not None:
                items = (
                    getattr(list_flux, f"{FBC_v3}fluxObjective", None)
                    or getattr(list_flux, f"{FBC_v2}fluxObjective", None)
                    or getattr(list_flux, f"{FBC_v1}fluxObjective", None)
                )
                if items is not None:
                    for fobj in items:
                        rx_id = (
                            fobj.get(f"{FBC_v3}reaction")
                            or fobj.get(f"{FBC_v2}reaction")
                            or fobj.get(f"{FBC_v1}reaction")
                            or fobj.get("reaction")
                        )
                        coeff_str = (
                            fobj.get(f"{FBC_v3}coefficient")
                            or fobj.get(f"{FBC_v2}coefficient")
                            or fobj.get(f"{FBC_v1}coefficient")
                            or fobj.get("coefficient")
                            or "1"
                        )
                        try:
                            coeff = float(coeff_str)
                        except Exception:
                            coeff = 1.0

                        rx_obj = sbml_id_map.get(rx_id)
                        flux_objs.append(
                            momapy.sbml.core.FluxObjective(
                                reaction=rx_obj
                                if isinstance(rx_obj, momapy.sbml.core.Reaction)
                                else None,
                                reaction_id=rx_id,
                                coefficient=coeff,
                            )
                        )

            objective = momapy.sbml.core.Objective(
                id_=obj_id,
                type=obj_type.lower(),
                flux_objectives=frozenset(flux_objs),
            )

            if active_id is None or obj_id == active_id:
                model.objective = objective

            map_ids[objective].add(obj_id)

            if wa:
                anns = cls._make_annotations_from_sbml_element(sbml_obj)
                if anns:
                    map_ann[objective].update(anns)
            if wn:
                nts = cls._make_notes_from_sbml_element(sbml_obj)
                if nts:
                    map_notes[objective].add(nts)

            break

momapy.io.register_reader("sbml", SBMLReader)
