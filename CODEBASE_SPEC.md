# momapy — Codebase API Specification

Condensed module-by-module inventory of public classes and function signatures for fast orientation in future Claude Code sessions. Pairs with `CLAUDE.md` (which covers architecture, conventions, and I/O patterns); this file covers the *surface*.

**Scope**: every Python source file under `src/momapy/`. Private helpers (`_reading_*`, `_writing_*`) are included because CLAUDE.md marks their `make_*` functions as the module's public contract. Large glyph/shape families are summarized rather than enumerated exhaustively.

**When this drifts**: regenerate with the same three Explore-agent prompts used originally (see commit message referencing this file). Expect drift on every substantive refactor of core/, io/, or a format subtree.

---

## Core library (`src/momapy/core/` and top-level)

### `src/momapy/core/__init__.py`
Re-exports only.

### `src/momapy/core/elements.py`
Purpose: base element classes for maps, models, and layouts.

Classes:
- `Direction(enum.Enum)`, `HAlignment(enum.Enum)`, `VAlignment(enum.Enum)`
- `MapElement` — root of everything; `id_: str` (not part of equality/hash)
- `ModelElement(MapElement)` — tag class for model-level elements
- `LayoutElement(MapElement, ABC)` — visual elements
  - Methods: `bbox() -> Bbox`, `drawing_elements() -> list[DrawingElement]`, `children() -> list[LayoutElement]`, `childless() -> Self`, `descendants() -> list[LayoutElement]`, `flattened() -> list[LayoutElement]`, `equals(other, flattened=False, unordered=False) -> bool`, `contains(other) -> bool`, `to_geometry() -> list[Segment|Curve|Arc]`, `anchor_point(anchor_name: str) -> Point`

### `src/momapy/core/model.py`
Purpose: abstract `Model` base class.

- `Model(MapElement)` — abstract; `is_submodel(other) -> bool`.
  **Note**: `Model` extends `MapElement`, NOT `ModelElement`, in all formats (SBGN PD/AF, SBML, CellDesigner). Enforced by `tests/test_io_mappings.py`.

### `src/momapy/core/map.py`
Purpose: top-level `Map` combining model, layout, and mapping.

- `Map(MapElement)` — `model`, `layout`, `layout_model_mapping`; `is_submap(other) -> bool`, `get_mapping(map_element)`.

### `src/momapy/core/mapping.py`
Purpose: bidirectional layout↔model mappings.

- `LayoutModelMapping(FrozenSurjectionDict)` — immutable; `get_mapping(map_element)`, `is_submapping(other)`.
- `LayoutModelMappingBuilder(SurjectionDict, Builder)` — mutable; `add_mapping(layout_element, model_element, replace=False, anchor=None)`, `build(builder_to_object=None) -> LayoutModelMapping`, `from_object(obj, omit_keys=True, object_to_builder=None) -> Self`.

### `src/momapy/core/layout.py`
Purpose: visual layout element hierarchy.

- `TextLayout(LayoutElement)` — `text`, `position`, font styling, `fill`/`stroke`, alignment, `transform`.
- `Shape(LayoutElement)` — abstract geometric shape.
- `GroupLayout(LayoutElement)` — `elements: tuple[LayoutElement]`, `transform`, `group_transform`.
- `Node(GroupLayout)` — `position`, `width`, `height`, `fill`, `stroke`, `stroke_width`, `filter`; anchors `north/south/east/west/center() -> Point`.
- `Arc(GroupLayout)` — `segments: tuple[Segment|Curve|Arc]`, line styling.
  - `SingleHeadedArc(Arc)` / `DoubleHeadedArc(Arc)` — add arrowhead classes.
- `Layout(Node)` — root container for a map's layout tree.

### `src/momapy/core/fonts.py`
Purpose: font file lookup via uharfbuzz.

- `find_font(family: str, weight: FontWeight|int, style: FontStyle) -> str | None`
- Internal: `_FontEntry`, `_get_font_directories() -> list[str]`, `_read_font_metadata(path: str) -> list[_FontEntry]`.

### `src/momapy/core/builders.py`
Purpose: auto-generated builder classes for core elements.

Exports `MapElementBuilder`, `ModelElementBuilder`, `LayoutElementBuilder`, `NodeBuilder`, `SingleHeadedArcBuilder`, `DoubleHeadedArcBuilder`, `TextLayoutBuilder`, `ModelBuilder` (with `new_element`), `LayoutBuilder` (with `new_element`).

### `src/momapy/geometry.py`
Purpose: geometric primitives and affine transformations.

Classes: `GeometryObject(ABC)`, `Point`, `Line`, `Segment`, `QuadraticBezierCurve`, `CubicBezierCurve`, `EllipticalArc`, `Bbox`, `Transformation(ABC)`, `MatrixTransformation`, `Rotation`, `Translation`, `Scaling`.

Key `Point` methods: `__add__/sub/mul/truediv`, `to_matrix() -> ndarray`, `to_tuple() -> tuple[float, float]`, `get_intersection_with_line(line) -> list[Point]`, `get_angle_to_horizontal() -> float`, `transformed(transformation)`, `reversed()`, `round(ndigits=None)`, `bbox()`, `isnan()`, `from_tuple(t) -> Self`.

Key `Bbox` methods: `center()`, `bbox()`, `contains_point(point)`, `intersects_bbox(bbox)`, `union(other)`, `from_points(points)`.

Constants: `ROUNDING=4`, `ROUNDING_TOLERANCE`, `ZERO_TOLERANCE=1e-12`, `PARAMETER_TOLERANCE=1e-10`, `CONVERGENCE_TOLERANCE=1e-8`.

### `src/momapy/drawing.py`
Purpose: SVG-like drawing primitives and filter effects.

Classes: `NoneValueType`, `FilterEffect(ABC)` + (`DropShadowEffect`, `CompositeEffect`, `FloodEffect`, `GaussianBlurEffect`, `OffsetEffect`), `FilterEffectInput(Enum)`, `CompositionOperator(Enum)`, `EdgeMode(Enum)`, `Filter`, `FontStyle(Enum)`, `FontWeight(Enum)`, `TextAnchor(Enum)`, `FillRule(Enum)`, `DrawingElement(ABC)`, `Text(DrawingElement)`, `Group(DrawingElement)`, `PathAction(ABC)` + (`MoveTo`, `LineTo`, `EllipticalArc`, `CurveTo`, `QuadraticCurveTo`, `ClosePath`), `Path(DrawingElement)`, `Ellipse(DrawingElement)`, `Rectangle(DrawingElement)`.

Functions:
- `get_initial_value(attr_name: str) -> Any`
- `drawing_elements_to_geometry(elements) -> list[Segment|Curve|Arc]`

### `src/momapy/builder.py`
Purpose: automatic builder-class generation for frozen dataclasses.

Classes: `Builder(ABC, Monitored)` — `build(builder_to_object=None)`, `from_object(obj, omit_keys=True, object_to_builder=None) -> Self`.

Functions:
- `get_or_make_builder_cls(cls, builder_fields=None, builder_bases=None, builder_namespace=None) -> type[Builder]`
- `object_from_builder(obj, builder_to_object=None) -> Any`
- `builder_from_object(obj, omit_keys=True, object_to_builder=None) -> Builder`
- `isinstance_or_builder(obj, cls) -> bool`, `issubclass_or_builder(cls, parent) -> bool`
- `new_builder_object(cls, *args, **kwargs) -> Builder`
- `register_builder_cls(builder_cls)`

### `src/momapy/styling.py`
Purpose: CSS-like style sheets.

- `StyleCollection(dict)`, `StyleSheet(dict)` — `StyleSheet.from_file(path)`, `.from_string(s)`, `.from_files(paths)`, `__or__` merge.
- `combine_style_sheets(style_sheets) -> StyleSheet`
- `apply_style_collection(layout_element, style_collection, strict=True)`
- `apply_style_sheet(map_or_layout, style_sheet, strict=True)`

### `src/momapy/coloring.py`
Purpose: color type + ~150 named constants.

- `Color` — `red`, `green`, `blue`, `alpha=1.0`; `__or__(alpha)`, `to_rgba/to_rgb/to_hex/to_hexa`, `with_alpha`, `from_rgba/from_rgb/from_hex/from_hexa`.

### `src/momapy/positioning.py`
Purpose: relative positioning helpers.

- `right_of/left_of/above_of/below_of(obj, distance: float) -> Point`
- `fit(objs) -> Bbox`
- `set_position(obj, position: Point)` — in-place on a builder.

### `src/momapy/utils.py`
Purpose: container types and helpers.

- `SurjectionDict(dict)` — inverse via `.inverse`.
- `IdentitySurjectionDict(dict)` — inverse by `id()`.
- `FrozenSurjectionDict(frozendict.frozendict)` — immutable variant.
- `pretty_print(obj, max_depth=0, exclude_cls=None)`
- `make_uuid4_as_str() -> str`
- `cached_dataclass_eq(self, other) -> bool`

### `src/momapy/monitoring.py`
Purpose: event registration for mutable objects.

- `Event(ABC)` (has `obj`), `ChangedEvent(Event)`, `SetEvent(Event)`; `Monitored` mixin.
- `register_event(obj, event_cls, callback, attr_name=None)`, `trigger_event(event)`, `on_change(obj, callback, attr_name=None)`, `on_set(obj, callback, attr_name=None)`.

### `src/momapy/cli.py`
Purpose: `momapy` CLI.

- `main()` dispatches subcommands: `render`, `export`, `list`, `info`, `visualize`, `tidy`, `style`.
- Built-in presets registry `_BUILTIN_PRESETS` (cs_default, sbgned, newt, ...).

### `src/momapy/io/__init__.py`
- `get_reader(name) -> type[Reader]`, `get_writer(name) -> type[Writer]`, `list_readers() -> list[str]`, `list_writers() -> list[str]`.
- Module state: `reader_registry`, `writer_registry` (both `PluginRegistry`).

### `src/momapy/io/core.py`
Purpose: reader/writer base classes + dispatch.

- `IOResult` — `exceptions: list[Exception]`.
- `ReaderResult(IOResult)` — `obj`, `element_to_annotations`, `element_to_notes`, `id_to_element`, `source_id_to_model_element`, `source_id_to_layout_element`, `file_path`.
- `WriterResult(IOResult)` — `obj`, `file_path`.
- `Reader(ABC)` — `read(file_path, **options) -> ReaderResult`, `check_file(file_path) -> bool`.
- `Writer(ABC)` — `write(obj, file_path, **options) -> WriterResult`.
- Module: `read(file_path, reader=None, **options)`, `write(obj, file_path, writer, **options)`.

### `src/momapy/io/utils.py`
Purpose: reader-side helpers.

- `ReadingContext` — base context with `xml_root`, `map_key`, `model`, `layout`, `xml_id_to_model_element`, `xml_id_to_layout_element`, `layout_model_mapping`, `element_to_annotations`, `element_to_notes`, `with_annotations`, `with_notes`, `model_element_cache`, `model_element_remap`, `evicted_elements`.
- `collect_model_elements(model: Model) -> dict[str, ModelElement]` — recursively gathers every `ModelElement` reachable from a `Model` via frozenset/tuple fields; the `Model` itself is NOT included.
- `build_id_mappings(reading_context, frozen_obj, frozen_model, frozen_layout, real_model_source_ids=None, real_layout_source_ids=None) -> (frozendict, FrozenSurjectionDict|None, FrozenSurjectionDict|None)` — builds the three `ReaderResult` dicts.
- `register_model_element(reading_context, element, collection, source_id=None)` and related remap helpers.

### `src/momapy/plugins/core.py`
- `PluginRegistry(Generic[T])` — `register(name, plugin)`, `register_lazy(name, import_path)`, `get(name) -> T|None`, `is_available(name) -> bool`, `list_available() -> list[str]`.

### `src/momapy/meta/nodes.py`
Generic node classes (all extend `Node`): `Rectangle`, `Ellipse`, `Stadium`, `Hexagon`, `TurnedHexagon`, `Parallelogram`, `CrossPoint`, `Triangle`, `Diamond`, `Bar`. Configurable corner radii on rectangles; `direction`/`angle` fields on directional shapes.

### `src/momapy/meta/arcs.py`
Generic arc classes. Single-headed: `PolyLine` (no head), `Triangle`, `ReversedTriangle`, `Rectangle`, `Ellipse`, `Diamond`, `Bar`, `Circle`. Double-headed: `DoubleTriangle`, `DoubleTriangleNoStraight`, `DoubleTriangleBar`.

### `src/momapy/meta/shapes.py`
Shape classes (extend `Shape`, override `drawing_elements()`): `Rectangle`, `Ellipse`, `Stadium`, `Hexagon`, `TurnedHexagon`, `Triangle`, `Diamond`, `Parallelogram`, `RectangleWithSlantedSides`, `Pentagon`, `HexagonWithSlantedSides`, `Barrel`, plus several specialized shapes.

### `src/momapy/rendering/__init__.py`
- `get_renderer(name) -> type[Renderer]`, `list_renderers()`, `register_renderer(name, renderer_cls)`. Registry: `renderer_registry`.

### `src/momapy/rendering/core.py`
- `Renderer(ABC)` — class attr `supported_formats: list[str]`; `render_layout_element(element, file_path, format=None)`, `render(layout_element)`.
- `StatefulRenderer(Renderer, ABC)` — `begin_session()`, `end_session()`, `render_layout_element(element)`.
- Module: `render_layout_element(element, file_path, format=None, renderer=None, style_sheet=None, to_top_left=False)`, `render_layout_elements(elements, file_path, format=None, renderer=None, style_sheet=None, to_top_left=False, multi_pages=True)`.

### `src/momapy/rendering/cairo.py`
- `CairoRenderer(StatefulRenderer)` — formats: pdf, svg, png, ps. Requires pycairo/PyGObject. `from_file(file_path, width, height, format)`.

### `src/momapy/rendering/skia.py`
- `SkiaRenderer(StatefulRenderer)` — formats: pdf, svg, png, jpeg, webp. Requires skia-python. `from_file(file_path, width, height, format)`.

### `src/momapy/rendering/svg_native.py`
- `SVGElement` — manual SVG DOM; `to_string(indent=0)`, `add_element(element)`.
- `SVGNativeRenderer(Renderer)` — format: svg. `render(layout_element) -> str`.

---

## SBGN (`src/momapy/sbgn/`)

### `src/momapy/sbgn/core.py`
Purpose: shared SBGN bases for PD and AF.

- `SBGNModelElement(momapy.core.elements.ModelElement)`
- `SBGNAuxiliaryUnit(SBGNModelElement)`
- `SBGNRole(SBGNModelElement)` — `element: SBGNModelElement`.
- `SBGNModel(momapy.core.model.Model)` — shared model base.
- `SBGNLayout(momapy.core.layout.Layout)` — `fill: Color|None = white`.
- `SBGNMap(momapy.core.map.Map)` — `model: SBGNModel`, `layout: SBGNLayout`.
- `SBGNNode(Node)`, `SBGNSingleHeadedArc(SingleHeadedArc)`, `SBGNDoubleHeadedArc(DoubleHeadedArc)`.
- Mixins: `_ConnectorsMixin` (direction, left/right connector lengths), `_SBGNMixin` (drawing element factory).

### `src/momapy/sbgn/pd.py`
Purpose: SBGN Process Description — models + layouts.

Model families (one example each, then enumeration):

- **Auxiliary units**: `StateVariable(SBGNAuxiliaryUnit)` — `variable: str|None`, `value: str|None`, `order: int|None`; `UnitOfInformation` (`value: str`, `prefix: str|None`); `Subunit` base with per-type subclasses (`UnspecifiedEntitySubunit`, `MacromoleculeSubunit`, `NucleicAcidFeatureSubunit`, `SimpleChemicalSubunit`, `ComplexSubunit`, `MultimerSubunit`, `MacromoleculeMultimerSubunit`, `NucleicAcidFeatureMultimerSubunit`, `SimpleChemicalMultimerSubunit`, `ComplexMultimerSubunit`).
- **Compartment**: `Compartment(SBGNModelElement)` — `label`, `state_variables`, `units_of_information`.
- **Entity pools**: `EntityPool(SBGNModelElement)` base (`label`, `compartment`); subclasses `EmptySet`, `PerturbingAgent`, `UnspecifiedEntity`, `Macromolecule`, `NucleicAcidFeature`, `SimpleChemical`, `Complex`, `Multimer`, and the four multimer variants.
- **Flux roles**: `FluxRole(SBGNRole)` (`element: EntityPool`) → `Reactant`, `Product`.
- **Processes**: `Process(SBGNModelElement)` (`reactants`, `products`) → `StoichiometricProcess`, `Phenotype`. Stoichiometric → `GenericProcess`, `UncertainProcess`, `OmittedProcess`. Generic → `Association`, `Dissociation`.
- **Logical operators**: `LogicalOperator` (`inputs: frozenset[LogicalOperatorInput]`) → `OrOperator`, `AndOperator`, `NotOperator`. `LogicalOperatorInput` has `element: Union[EntityPool, Compartment, LogicalOperator]`.
- **Equivalence operators**: `EquivalenceOperator` (`inputs`, `outputs`), `EquivalenceOperatorInput/Output` roles.
- **Modulations**: `Modulation(SBGNModelElement)` (`source`, `target`) → `Inhibition`, `Stimulation`. Stimulation → `Catalysis`, `NecessaryStimulation`.
- **Tags/terminals/submaps**: `Tag` (`label`, `reference_target`), `TagReference`, `Terminal(SBGNAuxiliaryUnit)`, `TerminalReference`, `Submap` (`label`, `terminals: frozenset[Terminal]`).
- **Model**: `SBGNPDModel(SBGNModel)` — `compartments`, `entity_pools`, `processes`, `modulations`, `logical_operators`, `equivalence_operators`, `submaps`, `tags`.

Layout: `SBGNPDLayout`, plus per-element `*Layout` classes mirroring the model families, process layouts using `_ConnectorsMixin`, arc layouts for `Consumption`, `Production`, `Modulation`, `Stimulation`, `NecessaryStimulation`, `Catalysis`, `Inhibition`, `LogicArc`, `EquivalenceArc`. Map: `SBGNPDMap(SBGNMap)`.

### `src/momapy/sbgn/af.py`
Purpose: SBGN Activity Flow.

Model families:
- **Units of information**: `UnitOfInformation` (`label`) with subclasses `Macromolecule/NucleicAcidFeature/Complex/SimpleChemical/UnspecifiedEntity/Perturbation UnitOfInformation`.
- **Compartment**: `Compartment(SBGNModelElement)` — `label`, `units_of_information`.
- **Activities**: `Activity` (`label`, `compartment: Compartment|None`) → `BiologicalActivity` (+`units_of_information`), `Phenotype`.
- **Logical operators**: `LogicalOperator` → `OrOperator`, `AndOperator`, `NotOperator`, `DelayOperator`.
- **Influences**: `Influence` (`source`, `target: Activity`) → `UnknownInfluence`, `PositiveInfluence`, `NegativeInfluence`, `NecessaryStimulation`.
- **Tags/terminals/submaps**: same pattern as PD but AF-specific classes.
- **Model**: `SBGNAFModel(SBGNModel)` — `compartments`, `activities`, `influences`, `logical_operators`, `submaps`, `tags`.

Layout: `SBGNAFLayout`, activity layouts with `_ConnectorsMixin`, delay operator, UoI layouts, influence arcs, logic/equivalence arcs. Map: `SBGNAFMap(SBGNMap)`.

### `src/momapy/sbgn/utils.py`
Purpose: SBGN layout tidying.

Functions (all accept `SBGNMap | Builder`, return same):
- `set_compartments_to_fit_content(map_, xsep=0, ysep=0)`
- `set_complexes_to_fit_content(map_, xsep=0, ysep=0)`
- `set_submaps_to_fit_content(map_, xsep=0, ysep=0)`
- `set_nodes_to_fit_labels(map_, xsep=0, ysep=0, omit_width=False, omit_height=False, restrict_to=None, exclude=None)`
- `set_arcs_to_borders(map_)`
- `set_auxiliary_units_to_borders(map_)`
- `set_auxiliary_units_label_font_size(map_, font_size)`
- `set_layout_to_fit_content(map_, xsep=0, ysep=0)`
- `tidy(map_, auxiliary_units_omit_width=False, auxiliary_units_omit_height=False, nodes_xsep=4, nodes_ysep=4, auxiliary_units_xsep=2, auxiliary_units_ysep=2, complexes_xsep=10, complexes_ysep=10, compartments_xsep=25, compartments_ysep=25, layout_xsep=0, layout_ysep=0)`
- `sbgned_tidy(map_)`, `newt_tidy(map_)` — preset parameters.
- `get_info(map_: SBGNMap) -> dict`

### `src/momapy/sbgn/styling/__init__.py`
Module-level `StyleSheet` constants: `cs_default`, `cs_black_and_white`, `sbgned`, `newt`, `fs_shadows`.

### `src/momapy/sbgn/io/pickle.py`
- `SBGNPickleReader(Reader)` — `check_file`, `read(file_path, return_type="map", with_model=True, with_layout=True, with_annotations=True, with_notes=True)`.
- `SBGNPickleWriter(Writer)` — `write(obj, file_path, element_to_annotations=None, element_to_notes=None, id_to_element=None, source_id_to_model_element=None, source_id_to_layout_element=None)`.

### `src/momapy/sbgn/io/sbgnml/reader.py`
- `ReadingContext(momapy.io.utils.ReadingContext)` — adds `sbgnml_compartments`, `sbgnml_entity_pools`, `sbgnml_logical_operators`, `sbgnml_stoichiometric_processes`, `sbgnml_phenotypes`, `sbgnml_submaps`, `sbgnml_activities`, `sbgnml_modulations`, `sbgnml_tags`, `sbgnml_glyph_id_to_sbgnml_arcs`.
- `_SBGNMLReader(Reader)` — base; `read(file_path, return_type="map", with_model=True, with_layout=True, with_annotations=True, with_notes=True, with_styles=True, xsep=0, ysep=0)`.
- `_get_map_key(sbgnml_map)` (abstract), `_parse_sbgnml_map(reading_context)`.

### `src/momapy/sbgn/io/sbgnml/writer.py`
- `WritingContext` — `map_`, `element_to_annotations`, `element_to_notes`, `source_id_to_model_element`, `source_id_to_layout_element`, `with_annotations`, `with_notes`.
- `_get_layout_elements(writing_context, model_element)`, `_get_frozenset_keys(writing_context, model_element)`, `_get_child_layout_element(writing_context, child_model, parent_model)`.

### `src/momapy/sbgn/io/sbgnml/_reading_model.py` (`make_*` public contract)
- `make_annotations_from_element(sbgnml_element)`
- `make_notes_from_element(sbgnml_element)`
- `make_and_add_annotations_and_notes(reading_context, sbgnml_element, model_element)`
- `set_label(model_element, sbgnml_element)`, `set_compartment(model_element, sbgnml_element, sbgnml_id_to_model_element)`, `set_stoichiometry(model_element, sbgnml_stoichiometry)`
- `make_compartment(reading_context, sbgnml_compartment)`
- `make_entity_pool_or_subunit(reading_context, sbgnml_entity_pool_or_subunit, model_element_cls)`
- `make_activity(reading_context, sbgnml_activity, model_element_cls)`
- `make_state_variable(reading_context, sbgnml_state_variable, order=None)`
- `make_unit_of_information(reading_context, sbgnml_unit_of_information, model_element_cls)`
- (+ ~15 more for processes, roles, operators, influences, tags, terminals, submaps)

### `src/momapy/sbgn/io/sbgnml/_reading_layout.py` (`make_*`)
- `make_text_layout(text, position, font_size=11.0) -> TextLayout`
- `make_points(sbgnml_points) -> list[Point]`, `make_segments(points) -> list[Segment]`, `make_arc_segments(sbgnml_arc, reverse=False) -> list[Segment]`
- `make_stoichiometry_layout(sbgnml_stoichiometry, layout, layout_element)`
- `set_connector_lengths(layout_element, sbgnml_element)`, `set_position_and_size(layout_element, sbgnml_glyph)`
- `make_compartment(reading_context, sbgnml_compartment)`
- `make_entity_pool_or_subunit(reading_context, sbgnml_entity_pool_or_subunit, layout_element_cls)`
- (+ ~20 more for processes, arcs, logical operators, auxiliary units)

### `src/momapy/sbgn/io/sbgnml/_reading_parsing.py`
- `transform_class(sbgnml_class: str) -> str`
- `has_undefined_variable(sbgnml_state_variable) -> bool`
- `get_glyphs(sbgnml_element)`, `get_glyphs_recursively(sbgnml_element)`
- `get_arcs(sbgnml_element)`, `get_ports(sbgnml_element)`
- `get_nexts(sbgnml_arc)`, `get_sbgnml_points(sbgnml_arc)`
- `get_annotation(sbgnml_element)`, `get_notes(sbgnml_element)`, `get_rdf(sbgnml_element)`
- Sets: `_SBGNML_STATE_VARIABLE_CLASSES`, `_SBGNML_UNIT_OF_INFORMATION_CLASSES`, `_SBGNML_TERMINAL_CLASSES`, `_SBGNML_SUBUNIT_CLASSES`.

### `src/momapy/sbgn/io/sbgnml/_reading_classification.py`
- `KEY_TO_MODULE: dict` — `"PROCESS_DESCRIPTION"` → `momapy.sbgn.pd`, `"ACTIVITY_FLOW"` → `momapy.sbgn.af`.
- `KEY_TO_CLASS: dict[tuple|str, tuple[type, type]]` — ~100 entries like `("PROCESS_DESCRIPTION", "GLYPH", "MACROMOLECULE") -> (Macromolecule, MacromoleculeLayout)`.
- `get_module(map_key: str)`, `get_module_from_object(obj)`, `get_glyph_key(sbgnml_glyph, map_key)`, `get_arc_key(sbgnml_arc, map_key)`.

### `src/momapy/sbgn/io/sbgnml/_writing.py`
- `NSMAP: dict` — SBGN/RDF/BioModels XML namespaces.
- `make_lxml_element(tag, namespace=None, attributes=None, text=None, nsmap=None)`
- `get_sbgnml_id(map_element, source_id_to_layout_element) -> str`
- `make_sbgnml_bbox_from_node(node)`, `make_sbgnml_bbox_from_text_layout(text_layout)`
- `make_sbgnml_label(text_layout)`, `make_sbgnml_state(text_layout)`
- `make_sbgnml_port(point, port_id)`, `make_sbgnml_points(points)`
- `make_sbgnml_annotation(annotations, sbgnml_id)`, `add_annotations_and_notes(writing_context, sbgnml_element, model_element)`.

### `src/momapy/sbgn/io/sbgnml/_writing_classification.py`
- `CLASS_TO_SBGNML_CLASS: dict` — ~85 entries mapping momapy classes to SBGN-ML class-attribute strings.
- `DIRECTION_TO_SBGNML_ORIENTATION: dict` — `Direction` enum → orientation string.
- `REVERSED_ARC_TYPES: tuple` — Consumption, LogicArc, EquivalenceArc (reversed during serialization).

---

## CellDesigner (`src/momapy/celldesigner/`)

### `src/momapy/celldesigner/core.py`
Purpose: CellDesigner model + layout.

Model families (grouped, one example per family):

- **Base**: `CellDesignerModelElement(ModelElement)` — abstract.
- **Regions**: `Region(CellDesignerModelElement)` (`name`, `active=False`) → `ModificationSite`, `CodingRegion`, `RegulatoryRegion`, `TranscriptionStartingSiteL`, `TranscriptionStartingSiteR`, `ProteinBindingDomain`.
- **Templates**: `SpeciesTemplate(CellDesignerModelElement)` (`name`) → `ProteinTemplate` (`modification_residues: frozenset[ModificationResidue]`) → `GenericProteinTemplate`, `TruncatedProteinTemplate`, `ReceptorTemplate`, `IonChannelTemplate`. Also `GeneTemplate` (`regions`), `RNATemplate`, `AntisenseRNATemplate`.
- **Entity pool species**: `Species(SBML.Species, CellDesignerModelElement)` and concrete species `Protein` → `GenericProtein`, `TruncatedProtein`, `Receptor`, `IonChannel`; plus `Gene`, `RNA`, `AntisenseRNA`, `Phenotype`, `Ion`, `SimpleMolecule`, `Drug`, `Unknown`, `Degraded`, `Complex`.
- **Reaction participants**: `Reactant(SpeciesReference, CellDesignerModelElement)`, `Product(SpeciesReference, CellDesignerModelElement)`.
- **Reactions**: `Reaction(SBML.Reaction, CellDesignerModelElement)` → `StateTransition`, `KnownTransitionOmitted`, `UnknownTransition`, `Transcription`, `Translation`, `Transport`, `HeterodimerAssociation`, `Dissociation`, `Truncation`.
- **Modifiers / logic gates**: `BooleanLogicGate`, `BooleanLogicGateInput`; gate subclasses `AndGate`, `OrGate`, `NotGate`, `UnknownGate`. `KnownOrUnknownModulator` → `Modulator` → `Inhibitor`, `PhysicalStimulator`, `Catalyzer`, `Trigger`, `UnknownCatalyzer`, `UnknownInhibitor`; `UnknownModulator`.
- **Modulations**: `KnownOrUnknownModulation` → `Modulation` → `Catalysis`, `Inhibition`, `PhysicalStimulation`, `Triggering`, `PositiveInfluence`, `NegativeInfluence`; `UnknownModulation` → `UnknownCatalysis`, `UnknownInhibition`, `UnknownPositiveInfluence`, `UnknownNegativeInfluence`, `UnknownPhysicalStimulation`, `UnknownTriggering`.
- **Other**: `ModificationResidue` (`name`, `order`), `ModificationState(enum.Enum)` (PHOSPHORYLATED/ACETYLATED/UBIQUITINATED/... 13 values), `Modification`, `StructuralState`, `Compartment(SBML.Compartment, CellDesignerModelElement)`.

Layout families:
- Base: `CellDesignerNode` — provides `anchor_point`, `own_border`, compass methods.
- Protein/gene nodes: `GenericProteinLayout`/`*ActiveLayout`, `ReceptorLayout`/active, `IonChannelLayout`/active, `GeneLayout`/active, `RNALayout`/active, `AntisenseRNALayout`/active, `TruncatedProteinLayout`/active, `DrugLayout`/active.
- Other nodes: `PhenotypeLayout`/active, `IonLayout`/active, `SimpleMoleculeLayout`/active, `UnknownLayout`/active, `DegradedLayout`/active, `ComplexLayout`, `StructuralStateLayout`, `ModificationLayout`, `OvalCompartmentLayout`, `RectangleCompartmentLayout`.
- Arcs: `CellDesignerSingleHeadedArc` (modulation arcs: `CatalysisLayout`, `UnknownCatalysisLayout`, `InhibitionLayout`, `UnknownInhibitionLayout`, `PhysicalStimulationLayout`, `UnknownPhysicalStimulationLayout`, `ModulationLayout`, `UnknownModulationLayout`, `PositiveInfluenceLayout`, `UnknownPositiveInfluenceLayout`, `TriggeringLayout`, `UnknownTriggeringLayout`); `CellDesignerDoubleHeadedArc`; `ReactionLayout` → `StateTransitionLayout`, `KnownTransitionOmittedLayout`, `UnknownTransitionLayout`, `TranscriptionLayout`, `TranslationLayout`, `TransportLayout`, `HeterodimerAssociationLayout`, `DissociationLayout`, `TruncationLayout`; also `ConsumptionLayout`, `ProductionLayout`, `LogicArcLayout`.
- Gate layouts: `AndGateLayout`, `OrGateLayout`, `NotGateLayout`, `UnknownGateLayout`.
- Containers: `CellDesignerLayout(Layout)`, `CellDesignerMap(Map)`.

### `src/momapy/celldesigner/utils.py`
Functions (accept `CellDesignerMap | Builder`, return same):
- `highlight_layout_elements(map_, layout_elements)`
- `set_layout_to_fit_content(map_, xsep=0, ysep=0)`
- `set_nodes_to_fit_labels(map_, xsep=0, ysep=0, omit_width=False, omit_height=False, restrict_to=None, exclude=None)`
- `set_compartments_to_fit_content(map_, xsep=0, ysep=0)`
- `set_complexes_to_fit_content(map_, xsep=0, ysep=0)`
- `set_modifications_to_borders(map_)`
- `set_modifications_label_font_size(map_, font_size)`
- `set_arcs_to_borders(map_)`
- `straighten_arcs(map_, angle_tolerance=5.0)`
- `tidy(map_, modifications_omit_width=False, modifications_omit_height=False, nodes_xsep=4, nodes_ysep=4, modifications_xsep=2, modifications_ysep=2, complexes_xsep=10, complexes_ysep=10, compartments_xsep=25, compartments_ysep=25, layout_xsep=0, layout_ysep=0, arcs_angle_tolerance=5.0)`
- `get_info(map_) -> dict`

### `src/momapy/celldesigner/io/pickle.py`
- `CellDesignerPickleReader(Reader)` — `read(file_path, return_type="map", with_model=True, with_layout=True, with_annotations=True, with_notes=True)`.
- `CellDesignerPickleWriter(Writer)` — same writer signature family as SBGN.

### `src/momapy/celldesigner/io/celldesigner/reader.py`
- `ReadingContext(ReadingContext)` — model/layout/map state, classified lists (cd_compartments, cd_compartment_aliases, cd_species_templates, cd_species_aliases, cd_reactions, cd_modulations), ID caches, `real_model_source_ids` + `real_layout_source_ids` (split for `ReaderResult.source_id_to_model_element` vs `_layout_element`).
- `CellDesignerReader(Reader)` — `read(file_path, return_type="map", with_model=True, with_layout=True, with_annotations=True, with_notes=True)`.
- Key internal classification map: `_KEY_TO_CLASS` (tuple keys for templates/species/reactions to momapy classes).

### `src/momapy/celldesigner/io/celldesigner/writer.py`
- `WritingContext` — `map_`, metadata dicts, `subunit_to_complex`, `used_metaids`, `species_to_id`.
- `CellDesignerWriter(Writer)` — `write(obj, file_path, element_to_annotations=None, element_to_notes=None, id_to_element=None, source_id_to_model_element=None, source_id_to_layout_element=None)`.

### `src/momapy/celldesigner/io/celldesigner/_reading_model.py` (`make_*`)
- `make_annotations_from_element(cd_element)`, `make_annotations_from_notes(cd_notes)`, `make_notes_from_element(cd_element)`, `make_and_add_annotations(reading_context, cd_element, model_element)`
- `make_empty_model(cd_element)`, `make_empty_map(cd_element)`
- `make_compartment(reading_context, cd_compartment)`
- `make_species_template(reading_context, cd_species_template, model_element_cls)`
- `make_modification_residue(reading_context, cd_modification_residue, super_cd_element, order)`
- `make_region(reading_context, cd_region, model_element_cls, super_cd_element, order)`
- `make_species(reading_context, cd_species, model_element_cls)`
- `make_species_modification(reading_context, cd_species_modification)`
- `make_species_structural_state(reading_context, cd_species_structural_state)`
- `make_reaction(reading_context, cd_reaction, model_element_cls)`
- `make_reactant_from_base(reading_context, cd_base_reactant, cd_reaction)` / `make_reactant_from_link(...)`
- `make_product_from_base(...)` / `make_product_from_link(...)`
- `make_modifier(reading_context, model_element_cls, source_model_element, metaid)`
- `make_logic_gate(reading_context, model_element_cls)`, `make_logic_gate_input(reading_context, input_model_element)`
- `make_modulation(reading_context, model_element_cls)`

### `src/momapy/celldesigner/io/celldesigner/_reading_layout.py` (`make_*`)
- `make_empty_layout(cd_element)`
- `make_segments(points)`, `make_points(cd_edit_points)`
- `make_species(reading_context, cd_species, ...)`, `make_species_modification(...)`, `make_species_structural_state(...)`
- `make_compartment_from_alias(reading_context, cd_compartment, cd_compartment_alias)`
- `make_segments_non_t_shape(reading_context, cd_reaction)`, `make_segments_left_t_shape(...)`, `make_segments_right_t_shape(...)`
- `make_reaction(reading_context, cd_reaction, ...)`
- `make_reactant_from_base(...)` / `make_reactant_from_link(...)`, `make_product_from_base(...)` / `make_product_from_link(...)`
- `make_modifier(reading_context, ...)`
- `make_logic_gate(reading_context, cd_element, layout_element_cls)`, `make_logic_arc(reading_context, gate_layout_element, input_layout_element)`
- `make_modulation(reading_context, ...)`

### `src/momapy/celldesigner/io/celldesigner/_reading_parsing.py`
- `make_name(name: str|None) -> str|None`
- `make_id_to_element_mapping(cd_model) -> dict`
- `make_complex_alias_to_included_ids_mapping(cd_model) -> dict`
- Constant: `_LINK_ANCHOR_POSITION_TO_ANCHOR_NAME`.

### `src/momapy/celldesigner/io/celldesigner/_writing.py`
- `make_cd_element(tag, ns=None, attributes=None, text=None)` — namespaced XML element factory.

---

## SBML (`src/momapy/sbml/`)

### `src/momapy/sbml/core.py`
Purpose: SBML core types and BioModels annotation enums.

- `BiomodelQualifier(Enum)` (abstract), `BQModel(BiomodelQualifier)` (HAS_INSTANCE, IS, IS_DERIVED_FROM, IS_DESCRIBED_BY, IS_INSTANCE_OF), `BQBiol(BiomodelQualifier)` (ENCODES, HAS_PART, HAS_PROPERTY, HAS_VERSION, IS, IS_DESCRIBED_BY, IS_ENCODED_BY, IS_HOMOLOG_TO, IS_PART_OF, IS_PROPERTY_OF, IS_VERSION_OF, OCCURS_IN, HAS_TAXON).
- `SBMLModelElement(momapy.core.elements.ModelElement)` — abstract; `name: str|None`, `sbo_term: SBOTerm|None`, `metaid: str|None (compare=False, hash=False)`. **(Formerly named `SBase`; renamed so that `Model` is never a `ModelElement` — see `tests/test_io_mappings.py`.)**
- `RDFAnnotation(ModelElement)` — `qualifier`, `resources: frozenset[str]`.
- `SBOTerm(ModelElement)` — placeholder.
- `Compartment(SBMLModelElement)` — `outside: Compartment|None`.
- `Species(SBMLModelElement)` — `compartment: Compartment|None`.
- `SimpleSpeciesReference(SBMLModelElement)` — `referred_species: Species`.
- `ModifierSpeciesReference(SimpleSpeciesReference)`.
- `SpeciesReference(SimpleSpeciesReference)` — `stoichiometry: float|None`.
- `Reaction(SBMLModelElement)` — `reversible`, `compartment`, `reactants`, `products`, `modifiers`.
- `SBMLModel(momapy.core.model.Model)` — **does NOT inherit `SBMLModelElement`**; declares its own `name`, `sbo_term`, `metaid`, plus `compartments`, `species`, `reactions`. `is_submodel(other)`.
- `SBML(SBMLModelElement)` — root; `xmlns`, `level=3`, `version=2`, `model: SBMLModel|None`.
- `SBMLModelBuilder` (auto-generated).

### `src/momapy/sbml/io/sbml/reader.py`
- `ReadingContext` — `sbml_model`, `model`, `sbml_id_to_model_element`, `sbml_id_to_sbml_element`, `element_to_annotations`, `element_to_notes`, `map_element_to_ids`, `with_annotations`, `with_notes`.
- `SBMLReader(Reader)` — `read(file_path, with_annotations=True, with_notes=True)`.

### `src/momapy/sbml/io/sbml/_model.py` (`make_*`)
- `make_annotations(rdf)`, `make_notes(notes_element)`, `make_annotations_from_element(sbml_element)`, `make_notes_from_element(sbml_element)`
- `make_empty_model(sbml_element)`
- `make_compartment(sbml_compartment, model)`
- `make_species(sbml_species, model, sbml_id_to_model_element)`
- `make_reaction(sbml_reaction, model)`
- `make_species_reference(sbml_species_reference, model, sbml_id_to_model_element)`
- `make_modifier_species_reference(sbml_modifier_species_reference, model, sbml_id_to_model_element)`

### `src/momapy/sbml/io/sbml/_parsing.py`
- `make_id_to_element_mapping(sbml_model) -> dict`.

### `src/momapy/sbml/io/sbml/_qualifiers.py`
- `QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE` — `BQBiol`/`BQModel` → `(namespace_url, local_name)`.
- `QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER` — reverse.

---

## Cross-cutting reminders

- **Frozen dataclasses everywhere**: mutate only via builders (`builder_from_object` → change → `build()`).
- **`Model` is a `MapElement`, never a `ModelElement`** in any format. `collect_model_elements(model)` traverses `Model` directly by field walking, and the `Model` itself is excluded from its own element set.
- **Equality on elements**: structural (all fields except `id_`, `metaid`); dedup during read relies on it.
- **I/O `make_*` functions** are the public contract of `_reading_*` / `_writing_*` modules despite the underscore filenames.
- **ReaderResult public dicts**: `id_to_element`, `source_id_to_model_element`, `source_id_to_layout_element` — the SBGN and CellDesigner readers populate both `source_id_to_*` dicts; the split ensures alias ids appear only on the layout side and SBML ids only on the model side for CellDesigner (via `real_model_source_ids` / `real_layout_source_ids` in `build_id_mappings`).
