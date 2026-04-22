# momapy — API Reference

Condensed module-by-module inventory of public classes and function signatures for fast orientation in future Claude Code sessions. Pairs with `CLAUDE.md` (which covers architecture, conventions, and I/O patterns); this file covers the *surface*.

**Scope**: every Python source file under `src/momapy/`. Private helpers (`_reading_*`, `_writing_*`) are included because CLAUDE.md marks their `make_*` functions as the module's public contract. Large glyph/shape families are summarized rather than enumerated exhaustively.

**When this drifts**: regenerate by launching three Explore agents in parallel (one for `core/` + top-level + `meta/` + `rendering/` + `io/` + `plugins/`, one for `sbgn/*`, one for `celldesigner/*` + `sbml/*`), asking each for signatures as-written in this same Markdown format. Include `make_*` private helpers — they are the public contract of the `_reading_*`/`_writing_*` modules per CLAUDE.md. Expect drift on every substantive refactor of `core/`, `io/`, or a format subtree.

---

## Core library (`src/momapy/core/` and top-level)

### `src/momapy/core/__init__.py`
Re-exports: `Direction`, `HAlignment`, `VAlignment`, `MapElement`, `ModelElement`, `LayoutElement`, `Model`, `Map`, `LayoutModelMapping`, `LayoutModelMappingBuilder`, `TextLayout`, `Shape`, `GroupLayout`, `Node`, `Arc`, `SingleHeadedArc`, `DoubleHeadedArc`, `Layout`, `find_font`.

### `src/momapy/core/elements.py`
Purpose: base element classes for maps, models, and layouts.

Classes:
- `Direction(enum.Enum)`, `HAlignment(enum.Enum)`, `VAlignment(enum.Enum)`
- `MapElement` — root of everything; `id_: str` (not part of equality/hash).
- `ModelElement(MapElement)` — base for model-level elements; `descendants() -> list[ModelElement]` walks reachable model elements via scalar refs and `frozenset`/`tuple` fields, deduped by identity, excluding `self`.
- `LayoutElement(MapElement, ABC)` — visual elements; `bbox() -> Bbox`, `drawing_elements() -> list[DrawingElement]`, `children() -> list[LayoutElement]`, `childless() -> Self`, `descendants() -> list[LayoutElement]`, `flattened() -> list[LayoutElement]`, `equals(other, flattened=False, unordered=False) -> bool`, `contains(other) -> bool`, `to_geometry() -> list[Segment|Curve|Arc]`, `anchor_point(anchor_name: str) -> Point`.

### `src/momapy/core/model.py`
- `Model(MapElement)` — abstract; `is_submodel(other) -> bool`, `descendants() -> list[ModelElement]` (same walk as `ModelElement.descendants()`, seeded from the `Model`'s fields). **Note**: `Model` extends `MapElement`, NOT `ModelElement`, in all formats. Enforced by `tests/test_io_mappings.py`.

### `src/momapy/core/map.py`
- `Map(MapElement)` — `model`, `layout`, `layout_model_mapping`; `is_submap(other) -> bool`, `get_mapping(map_element)`.

### `src/momapy/core/mapping.py`
- `LayoutModelMapping(FrozenSurjectionDict)` — immutable; `get_mapping(map_element)`, `get_child_layout_elements(child_model_element, parent_model_element) -> list[LayoutElement]`, `is_submapping(other)`. Carries `_singleton_to_key: FrozenSurjectionDict` mapping each frozenset anchor to its frozenset key.
- `LayoutModelMappingBuilder(SurjectionDict, Builder)` — mutable; `get_mapping(map_element)`, `get_child_layout_elements(child_model_element, parent_model_element) -> list[LayoutElement]`, `add_mapping(layout_element, model_element, replace=False, anchor=None)`, `build(builder_to_object=None) -> LayoutModelMapping`, `from_object(obj, omit_keys=True, object_to_builder=None) -> Self`. Carries `_singleton_to_key: SurjectionDict`.

### `src/momapy/core/layout.py`
- `TextLayout(LayoutElement)` — `text`, `position`, font styling, `fill`/`stroke`, alignment, `transform`.
- `Shape(LayoutElement)` — abstract geometric shape.
- `GroupLayout(LayoutElement)` — `elements: tuple[LayoutElement]`, `transform`, `group_transform`.
- `Node(GroupLayout)` — `position`, `width`, `height`, `fill`, `stroke`, `stroke_width`, `filter`; anchors `north/south/east/west/center() -> Point`.
- `Arc(GroupLayout)` — `segments: tuple[Segment|Curve|Arc]`, line styling.
- `SingleHeadedArc(Arc)` / `DoubleHeadedArc(Arc)` — add arrowhead classes.
- `Layout(Node)` — root container for a map's layout tree.

### `src/momapy/core/fonts.py`
- `find_font(family: str, weight: FontWeight|int, style: FontStyle) -> str | None`.
- Internal: `_FontEntry`, `_get_font_directories() -> list[str]`, `_read_font_metadata(path: str) -> list[_FontEntry]`.

### `src/momapy/geometry.py`
Classes: `GeometryObject(ABC)`, `Point`, `Line`, `Segment`, `QuadraticBezierCurve`, `CubicBezierCurve`, `EllipticalArc`, `Bbox`, `Transformation(ABC)`, `MatrixTransformation`, `Rotation`, `Translation`, `Scaling`.

Key `Point` methods: `__add__/sub/mul/truediv`, `to_matrix() -> ndarray`, `to_tuple() -> tuple[float, float]`, `get_intersection_with_line(line) -> list[Point]`, `get_angle_to_horizontal() -> float`, `transformed(transformation)`, `reversed()`, `round(ndigits=None)`, `bbox()`, `isnan()`, `from_tuple(t) -> Self`.

Key `Bbox` methods: `center()`, `bbox()`, `contains_point(point)`, `intersects_bbox(bbox)`, `union(other)`, `from_points(points)`.

Constants: `ROUNDING=4`, `ROUNDING_TOLERANCE`, `ZERO_TOLERANCE=1e-12`, `PARAMETER_TOLERANCE=1e-10`, `CONVERGENCE_TOLERANCE=1e-8`.

### `src/momapy/drawing.py`
Classes: `NoneValueType`, `FilterEffect(ABC)` + (`DropShadowEffect`, `CompositeEffect`, `FloodEffect`, `GaussianBlurEffect`, `OffsetEffect`), `FilterEffectInput(Enum)`, `CompositionOperator(Enum)`, `EdgeMode(Enum)`, `Filter`, `FontStyle(Enum)`, `FontWeight(Enum)`, `TextAnchor(Enum)`, `FillRule(Enum)`, `DrawingElement(ABC)`, `Text(DrawingElement)`, `Group(DrawingElement)`, `PathAction(ABC)` + (`MoveTo`, `LineTo`, `EllipticalArc`, `CurveTo`, `QuadraticCurveTo`, `ClosePath`), `Path(DrawingElement)`, `Ellipse(DrawingElement)`, `Rectangle(DrawingElement)`.

Functions: `get_initial_value(attr_name: str) -> Any`, `drawing_elements_to_geometry(elements) -> list[Segment|Curve|Arc]`.

### `src/momapy/builder.py`
- `Builder(ABC, Monitored)` — `build(builder_to_object=None)`, `from_object(obj, omit_keys=True, object_to_builder=None) -> Self`.
- `get_or_make_builder_cls(cls, builder_fields=None, builder_bases=None, builder_namespace=None) -> type[Builder]`
- `object_from_builder(obj, builder_to_object=None) -> Any`
- `builder_from_object(obj, omit_keys=True, object_to_builder=None) -> Builder`
- `isinstance_or_builder(obj, cls) -> bool`, `issubclass_or_builder(cls, parent) -> bool`
- `new_builder_object(cls, *args, **kwargs) -> Builder`
- `register_builder_cls(builder_cls)`

### `src/momapy/styling/__init__.py`
Re-exports: `StyleCollection`, `StyleSheet`, `Selector`, `TypeSelector`, `ClassSelector`, `IdSelector`, `ChildSelector`, `DescendantSelector`, `OrSelector`, `CompoundSelector`, `NotSelector`, `combine_style_sheets`, `apply_style_collection`, `apply_style_sheet`, `get_stylable_attributes`.

### `src/momapy/styling/core.py`
Purpose: CSS-like style sheets.

- `StyleCollection(dict)`, `StyleSheet(dict)` — `StyleSheet.from_file(path)`, `.from_string(s)`, `.from_files(paths)`, `__or__` merge.
- `Selector(ABC)` and concrete subclasses: `TypeSelector`, `ClassSelector`, `IdSelector`, `ChildSelector`, `DescendantSelector`, `OrSelector`, `CompoundSelector`, `NotSelector`.
- `combine_style_sheets(style_sheets) -> StyleSheet`
- `apply_style_collection(layout_element, style_collection, strict=True)`
- `apply_style_sheet(map_or_layout, style_sheet, strict=True)`
- `get_stylable_attributes(cls) -> list[str]`

### `src/momapy/coloring.py`
- `Color` — `red`, `green`, `blue`, `alpha=1.0`; `__or__(alpha)`, `to_rgba/to_rgb/to_hex/to_hexa`, `with_alpha`, `from_rgba/from_rgb/from_hex/from_hexa`. Plus ~150 named module-level constants.

### `src/momapy/positioning.py`
- `right_of/left_of/above_of/below_of(obj, distance: float) -> Point`
- `above_left_of/above_right_of/below_left_of/below_right_of(obj, distance1: float, distance2: float | None = None) -> Point`
- `fit(elements, xsep=0, ysep=0) -> Bbox`
- `mid_of(obj1, obj2) -> Point`
- `cross_vh_of/cross_hv_of(obj1, obj2) -> Point`
- `fraction_of(arc_layout_element, fraction: float) -> tuple[Point, float]`
- `set_position(obj, position: Point, anchor: str | None = None)`
- `set_right_of/set_left_of/set_above_of/set_below_of(obj1, obj2, distance, anchor=None)`
- `set_above_left_of/set_above_right_of/set_below_left_of/set_below_right_of(obj1, obj2, distance1, distance2=None, anchor=None)`
- `set_fit(obj, elements, xsep=0, ysep=0, anchor=None)`
- `set_fraction_of(obj, arc_layout_element, fraction, anchor=None)`
- `set_mid_of(obj1, obj2, obj3, anchor=None)`
- `set_cross_hv_of/set_cross_vh_of(obj1, obj2, obj3, anchor=None)`

### `src/momapy/utils.py`
- `SurjectionDict(dict)` — inverse via `.inverse`.
- `IdentitySurjectionDict(dict)` — inverse by `id()`.
- `FrozenSurjectionDict(frozendict.frozendict)` — immutable variant.
- `pretty_print(obj, max_depth=0, exclude_cls=None)`
- `make_uuid4_as_str() -> str`
- `cached_dataclass_eq(self, other) -> bool`

### `src/momapy/monitoring.py`
- `Event(ABC)` (has `obj`), `ChangedEvent(Event)`, `SetEvent(Event)`; `Monitored` mixin.
- `register_event(obj, event_cls, callback, attr_name=None)`, `trigger_event(event)`, `on_change(obj, callback, attr_name=None)`, `on_set(obj, callback, attr_name=None)`.

### `src/momapy/cli.py`
- `main()` dispatches subcommands: `render`, `export`, `list`, `info`, `visualize`, `tidy`, `style`.
- Built-in presets registry `_BUILTIN_PRESETS` (cs_default, sbgned, newt, ...).

---

## I/O (`src/momapy/io/`)

### `src/momapy/io/__init__.py`
- `get_reader(name) -> type[Reader]`, `get_writer(name) -> type[Writer]`, `list_readers() -> list[str]`, `list_writers() -> list[str]`.
- `read(file_path, reader=None, **options)`, `write(obj, file_path, writer, **options)`.
- `register_reader(name, cls)`, `register_lazy_reader(name, import_path)`, `register_writer(name, cls)`, `register_lazy_writer(name, import_path)`.
- Module state: `reader_registry`, `writer_registry` (both `PluginRegistry`).

### `src/momapy/io/core.py`
Purpose: reader/writer base classes + dispatch.

- `IOResult` — base class for I/O results.
- `ReaderResult(IOResult)` — `obj`, `element_to_annotations`, `element_to_notes`, `id_to_element`, `source_id_to_model_element`, `source_id_to_layout_element`, `file_path`.
- `WriterResult(IOResult)` — `obj`, `file_path`.
- `Reader(ABC)` — `read(file_path, **options) -> ReaderResult`, `check_file(file_path) -> bool`.
- `Writer(ABC)` — `write(obj, file_path, **options) -> WriterResult`.

### `src/momapy/io/utils.py`
Purpose: reader-side helpers; shared base contexts.

- `ReadingContext` — base context with `xml_root`, `map_key`, `model`, `layout`, `xml_id_to_model_element`, `xml_id_to_layout_element`, `layout_model_mapping`, `element_to_annotations`, `element_to_notes`, `with_annotations`, `with_notes`, `model_element_cache`, `model_element_remap`, `evicted_elements`.
- `WritingContext` — base context with `map_`, `element_to_annotations`, `element_to_notes`, `source_id_to_model_element`, `source_id_to_layout_element`, `with_annotations`, `with_notes`.
- `build_id_mappings(reading_context, obj, real_model_source_ids=None, real_layout_source_ids=None) -> (frozendict, FrozenSurjectionDict|None, FrozenSurjectionDict|None)` — builds the three `ReaderResult` dicts. Dispatches `obj` internally: `Map` → uses its `.model`/`.layout`; `Model`/`Layout` → treated as the model/layout itself.
- `register_model_element(reading_context, element, collection, source_id=None)` and related remap helpers.

### `src/momapy/io/pickle.py`
Purpose: format-agnostic pickle reader/writer. Registered as `"pickle"` in `momapy.io`.

- `PickleReader(Reader)` — `check_file`, `read(file_path, return_type="map", with_model=True, with_layout=True, with_annotations=True, with_notes=True)`.
- `PickleWriter(Writer)` — `write(obj, file_path, element_to_annotations=None, element_to_notes=None, id_to_element=None, source_id_to_model_element=None, source_id_to_layout_element=None)`.

---

## Plugins (`src/momapy/plugins/`)

### `src/momapy/plugins/core.py`
- `PluginRegistry(Generic[T])` — `register(name, plugin)`, `register_lazy(name, import_path)`, `get(name) -> T|None`, `is_available(name) -> bool`, `list_available() -> list[str]`, `list_loaded() -> list[str]`.

---

## Meta shapes (`src/momapy/meta/`)

### `src/momapy/meta/nodes.py`
Generic node classes (all extend `Node`): `Rectangle`, `Ellipse`, `Stadium`, `Hexagon`, `TurnedHexagon`, `Parallelogram`, `CrossPoint`, `Triangle`, `Diamond`, `Bar`. Configurable corner radii on rectangles; `direction`/`angle` fields on directional shapes.

### `src/momapy/meta/arcs.py`
Generic arc classes. Single-headed: `PolyLine` (no head), `Triangle`, `ReversedTriangle`, `Rectangle`, `Ellipse`, `Diamond`, `Bar`, `Circle`. Double-headed: `DoubleTriangle`, `DoubleTriangleNoStraight`, `DoubleTriangleBar`.

### `src/momapy/meta/shapes.py`
Shape classes (extend `Shape`, override `drawing_elements()`): `Rectangle`, `Ellipse`, `Stadium`, `Hexagon`, `TurnedHexagon`, `Triangle`, `Diamond`, `Parallelogram`, `RectangleWithSlantedSides`, `Pentagon`, `HexagonWithSlantedSides`, `Barrel`, plus several specialized shapes.

---

## Rendering (`src/momapy/rendering/`)

### `src/momapy/rendering/__init__.py`
- `get_renderer(name) -> type[Renderer]`, `list_renderers() -> list[str]`, `register_renderer(name, renderer_cls)`, `register_lazy_renderer(name, import_path)`. Registry: `renderer_registry`.
- `render_layout_element(element, file_path, format=None, renderer=None, style_sheet=None, to_top_left=False)`
- `render_layout_elements(elements, file_path, format=None, renderer=None, style_sheet=None, to_top_left=False, multi_pages=True)`
- `render_map(map, file_path, format=None, renderer=None, style_sheet=None, to_top_left=False)`
- `render_maps(maps, file_path, format=None, renderer=None, style_sheet=None, to_top_left=False, multi_pages=True)`

### `src/momapy/rendering/core.py`
- `Renderer(ABC)` — class attr `supported_formats: list[str]`; `render_layout_element(element, file_path, format=None)`, `render(layout_element)`.
- `StatefulRenderer(Renderer, ABC)` — `begin_session()`, `end_session()`, `render_layout_element(element)`.

### `src/momapy/rendering/cairo.py`
- `CairoRenderer(StatefulRenderer)` — formats: pdf, svg, png, ps. Requires pycairo/PyGObject. `from_file(file_path, width, height, format)`.

### `src/momapy/rendering/skia.py`
- `SkiaRenderer(StatefulRenderer)` — formats: pdf, svg, png, jpeg, webp. Requires skia-python. `from_file(file_path, width, height, format)`.

### `src/momapy/rendering/svg_native.py`
- `SVGElement` — manual SVG DOM; `to_string(indent=0)`, `add_element(element)`.
- `SVGNativeRenderer(Renderer)` — format: svg. `render(layout_element) -> str`.

---

## SBGN (`src/momapy/sbgn/`)

### `src/momapy/sbgn/__init__.py`
Re-exports: `SBGNAuxiliaryUnit`, `SBGNDoubleHeadedArc`, `SBGNLayout`, `SBGNMap`, `SBGNModel`, `SBGNModelElement`, `SBGNNode`, `SBGNRole`, `SBGNSingleHeadedArc`.

### `src/momapy/sbgn/elements.py`
Purpose: shared SBGN bases and mixins for PD and AF.

- `SBGNModelElement(ModelElement)` — base for SBGN model elements.
- `SBGNAuxiliaryUnit(SBGNModelElement)` — base for state variables, units of information, terminals, tags.
- `SBGNRole(SBGNModelElement)` — `element: SBGNModelElement`.
- `SBGNNode(Node)` — base for SBGN glyphs; `fill`, `stroke`, `stroke_width`.
- `SBGNSingleHeadedArc(SingleHeadedArc)` — arc with one arrowhead; `arrowhead_*`, `path_*` styling fields.
- `SBGNDoubleHeadedArc(DoubleHeadedArc)` — arc with two arrowheads; `start_arrowhead_*`, `end_arrowhead_*`, `path_*`.
- `_ConnectorsMixin` — private mixin for process nodes; `direction`, `left_to_right`, `left_connector_length`, `right_connector_length`, per-connector styling.

### `src/momapy/sbgn/model.py`
- `SBGNModel(Model)` — abstract base shared by PD and AF.

### `src/momapy/sbgn/layout.py`
- `SBGNLayout(Layout)` — abstract base; `fill: Color | None = white`.

### `src/momapy/sbgn/map.py`
- `SBGNMap(Map)` — abstract base; `model: SBGNModel`, `layout: SBGNLayout`.

### `src/momapy/sbgn/utils.py`
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

### `src/momapy/sbgn/pd/__init__.py`
Re-exports: auxiliary units (`StateVariable`, `UnitOfInformation`, `Subunit` family), `Compartment`, entity pools (`EntityPool`, `EmptySet`, `PerturbingAgent`, `UnspecifiedEntity`, `Macromolecule`, `NucleicAcidFeature`, `SimpleChemical`, `Complex`, `Multimer` family), flux roles (`FluxRole`, `Reactant`, `Product`), logical operators (`LogicalOperator`, `OrOperator`, `AndOperator`, `NotOperator`, `LogicalOperatorInput`), equivalence operators (`EquivalenceOperator`, `EquivalenceOperatorInput`, `EquivalenceOperatorOutput`), processes (`Process`, `StoichiometricProcess`, `GenericProcess`, `UncertainProcess`, `Association`, `Dissociation`, `OmittedProcess`, `Phenotype`), modulations (`Modulation`, `Inhibition`, `Stimulation`, `Catalysis`, `NecessaryStimulation`), tags/terminals/submaps (`Tag`, `TagReference`, `Terminal`, `TerminalReference`, `Submap`), `SBGNPDModel`, all `*Layout` variants, `SBGNPDMap`.

### `src/momapy/sbgn/pd/model.py`
Purpose: SBGN-PD model classes.

- **Auxiliary units**: `StateVariable(SBGNAuxiliaryUnit)` — `variable`, `value`, `order`; `UnitOfInformation` — `value`, `prefix`; `Subunit` family with per-type subclasses (`UnspecifiedEntitySubunit`, `MacromoleculeSubunit`, `NucleicAcidFeatureSubunit`, `SimpleChemicalSubunit`, `ComplexSubunit`, `MultimerSubunit` (+ `cardinality`) and the four multimer variants).
- **Compartment**: `Compartment(SBGNModelElement)` — `label`, `state_variables`, `units_of_information`.
- **Entity pools**: `EntityPool(SBGNModelElement)` (`compartment`); subclasses `EmptySet`, `PerturbingAgent`, `UnspecifiedEntity`, `Macromolecule`, `NucleicAcidFeature`, `SimpleChemical`, `Complex` (+ `subunits`), `Multimer(Complex)` (+ `cardinality`) and the four multimer variants.
- **Flux roles**: `FluxRole(SBGNRole)` — `element: EntityPool`, `stoichiometry`; `Reactant`, `Product`.
- **Processes**: `Process(SBGNModelElement)` (`reactants`, `products`); `StoichiometricProcess` → `GenericProcess`, `UncertainProcess`, `OmittedProcess`; `GenericProcess` → `Association`, `Dissociation`; `Phenotype(Process)`.
- **Logical operators**: `LogicalOperator(SBGNModelElement)` (`inputs: frozenset[LogicalOperatorInput]`) → `OrOperator`, `AndOperator`, `NotOperator`. `LogicalOperatorInput(SBGNRole)` — `element: EntityPool | Compartment | LogicalOperator`.
- **Equivalence operators**: `EquivalenceOperator` (`inputs`, `outputs`), `EquivalenceOperatorInput`, `EquivalenceOperatorOutput`.
- **Modulations**: `Modulation(SBGNModelElement)` (`source`, `target`) → `Inhibition`, `Stimulation`. `Stimulation` → `Catalysis`, `NecessaryStimulation`.
- **Tags/terminals/submaps**: `Tag(SBGNAuxiliaryUnit)` (`label`, `reference_target`), `TagReference(SBGNRole)`, `Terminal(SBGNAuxiliaryUnit)`, `TerminalReference(SBGNRole)`, `Submap(SBGNModelElement)` (`label`, `terminals`).
- **Model**: `SBGNPDModel(SBGNModel)` — `compartments`, `entity_pools`, `processes`, `modulations`, `logical_operators`, `equivalence_operators`, `submaps`, `tags`.

### `src/momapy/sbgn/pd/layout.py`
- `SBGNPDLayout(SBGNLayout)`; per-element `*Layout` classes mirroring the model families: auxiliary unit layouts (`StateVariableLayout`, `UnitOfInformationLayout`, `TerminalLayout`, `CardinalityLayout`, subunit layouts), compartment/submap layouts, entity pool node layouts, process layouts (with `_ConnectorsMixin`), operator layouts, arc layouts (`Consumption`, `Production`, `Modulation`, `Stimulation`, `NecessaryStimulation`, `Catalysis`, `Inhibition`, `LogicArc`, `EquivalenceArc`), tag layouts.

### `src/momapy/sbgn/pd/map.py`
- `SBGNPDMap(SBGNMap)` — combines `SBGNPDModel` and `SBGNPDLayout`.

### `src/momapy/sbgn/af/__init__.py`
Re-exports: AF unit-of-information family (`UnitOfInformation`, `MacromoleculeUnitOfInformation`, `NucleicAcidFeatureUnitOfInformation`, `ComplexUnitOfInformation`, `SimpleChemicalUnitOfInformation`, `UnspecifiedEntityUnitOfInformation`, `PerturbationUnitOfInformation`), `Compartment`, activities (`Activity`, `BiologicalActivity`, `Phenotype`), logical operators (`LogicalOperator`, `OrOperator`, `AndOperator`, `NotOperator`, `DelayOperator`, `LogicalOperatorInput`), influences (`Influence`, `UnknownInfluence`, `PositiveInfluence`, `NegativeInfluence`, `NecessaryStimulation`), tags/terminals/submaps, `SBGNAFModel`, layout classes, `SBGNAFMap`.

### `src/momapy/sbgn/af/model.py`
Purpose: SBGN-AF model classes.

- **Units of information**: `UnitOfInformation(SBGNModelElement)` (`label`) plus AF-specific subclasses: `MacromoleculeUnitOfInformation`, `NucleicAcidFeatureUnitOfInformation`, `ComplexUnitOfInformation`, `SimpleChemicalUnitOfInformation`, `UnspecifiedEntityUnitOfInformation`, `PerturbationUnitOfInformation`.
- **Compartment**: `Compartment(SBGNModelElement)` — `label`, `units_of_information`.
- **Activities**: `Activity(SBGNModelElement)` — `label`, `compartment`; `BiologicalActivity` (+ `units_of_information`), `Phenotype`.
- **Logical operators**: `LogicalOperator` (`inputs`) → `OrOperator`, `AndOperator`, `NotOperator`, `DelayOperator`. `LogicalOperatorInput(SBGNRole)` — `element: Activity | LogicalOperator`.
- **Influences**: `Influence(SBGNModelElement)` (`source`, `target: Activity`) → `UnknownInfluence`, `PositiveInfluence`, `NegativeInfluence`, `NecessaryStimulation`.
- **Tags/terminals/submaps**: same shape as PD, AF-specific classes.
- **Model**: `SBGNAFModel(SBGNModel)` — `compartments`, `activities`, `influences`, `logical_operators`, `submaps`, `tags`.

### `src/momapy/sbgn/af/layout.py`
- `SBGNAFLayout(SBGNLayout)`; activity layouts (with `_ConnectorsMixin`), `DelayOperatorLayout`, unit-of-information layouts, influence arc layouts (unknown/positive/negative/necessary stimulation), logic and equivalence arc layouts.

### `src/momapy/sbgn/af/map.py`
- `SBGNAFMap(SBGNMap)` — combines `SBGNAFModel` and `SBGNAFLayout`.

### `src/momapy/sbgn/io/sbgnml/reader.py`
- `SBGNMLReadingContext(ReadingContext)` — adds `sbgnml_compartments`, `sbgnml_entity_pools`, `sbgnml_logical_operators`, `sbgnml_stoichiometric_processes`, `sbgnml_phenotypes`, `sbgnml_submaps`, `sbgnml_activities`, `sbgnml_modulations`, `sbgnml_tags`, `sbgnml_glyph_id_to_sbgnml_arcs`.
- `_SBGNMLReader(Reader)` — base; `read(file_path, return_type="map", with_model=True, with_layout=True, with_annotations=True, with_notes=True, xsep=0, ysep=0)`.
- Registered as `sbgnml-0.2` (`SBGNML0_2Reader`) and `sbgnml-0.3` / `sbgnml` (`SBGNML0_3Reader`).

### `src/momapy/sbgn/io/sbgnml/writer.py`
- `SBGNML0_3Writer(Writer)` — registered as `sbgnml-0.3` and `sbgnml`.
- `_get_layout_elements(writing_context, model_element)`, `_get_frozenset_keys(writing_context, model_element)`, `_get_child_layout_element(writing_context, child_model, parent_model)`.

### `src/momapy/sbgn/io/sbgnml/_reading_model.py` (`make_*` public contract)
- `make_annotations_from_element(sbgnml_element)`, `make_notes_from_element(sbgnml_element)`, `make_and_add_annotations_and_notes(reading_context, sbgnml_element, model_element)`
- `set_label(model_element, sbgnml_element)`, `set_compartment(model_element, sbgnml_element, sbgnml_id_to_model_element)`, `set_stoichiometry(model_element, sbgnml_stoichiometry)`
- `make_compartment(reading_context, sbgnml_compartment)`
- `make_entity_pool_or_subunit(reading_context, sbgnml_entity_pool_or_subunit, model_element_cls)`
- `make_activity(reading_context, sbgnml_activity, model_element_cls)`
- `make_state_variable(reading_context, sbgnml_state_variable, order=None)`
- `make_unit_of_information(reading_context, sbgnml_unit_of_information, model_element_cls)`
- (+ ~15 more for processes, flux roles, logical operators, modulations, tags, terminals, submaps, AF influences)

### `src/momapy/sbgn/io/sbgnml/_reading_layout.py` (`make_*`)
- `make_text_layout(text, position, font_size=11.0) -> TextLayout`
- `make_points(sbgnml_points) -> list[Point]`, `make_segments(points) -> list[Segment]`, `make_arc_segments(sbgnml_arc, reverse=False) -> list[Segment]`
- `make_stoichiometry_layout(sbgnml_stoichiometry, layout, layout_element)`
- `set_connector_lengths(layout_element, sbgnml_element)`, `set_position_and_size(layout_element, sbgnml_glyph)`
- `make_compartment(reading_context, sbgnml_compartment)`
- `make_entity_pool_or_subunit(reading_context, sbgnml_entity_pool_or_subunit, layout_element_cls)`
- (+ ~20 more for processes, arcs, logical operators, auxiliary units, activities, influences)

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
- `get_glyph_key(sbgnml_glyph, map_key)`, `get_subglyph_key(sbgnml_subglyph, map_key)`, `get_arc_key(sbgnml_arc, map_key)`, `get_model_and_layout_classes(key)`, `get_module(map_key)`, `get_module_from_object(obj)`.

### `src/momapy/sbgn/io/sbgnml/_writing.py`
- `NSMAP: dict` — SBGN/RDF/BioModels XML namespaces.
- `make_lxml_element(tag, namespace=None, attributes=None, text=None, nsmap=None)`
- `get_sbgnml_id(map_element, source_id_to_layout_element) -> str`
- `make_sbgnml_bbox_from_node(node)`, `make_sbgnml_bbox_from_text_layout(text_layout)`
- `make_sbgnml_label(text_layout)`, `make_sbgnml_state(text_layout)`
- `make_sbgnml_port(point, port_id)`, `make_sbgnml_points(points)`
- `make_sbgnml_annotation(annotations, sbgnml_id)`, `add_annotations_and_notes(writing_context, sbgnml_element, model_element)`

### `src/momapy/sbgn/io/sbgnml/_writing_classification.py`
- `CLASS_TO_SBGNML_CLASS: dict` — ~85 entries mapping momapy layout classes to SBGN-ML class-attribute strings.
- `DIRECTION_TO_SBGNML_ORIENTATION: dict` — `Direction` enum → orientation string.
- `REVERSED_ARC_TYPES: tuple` — `ConsumptionLayout`, `LogicArcLayout` (PD + AF), `EquivalenceArcLayout` (reversed during serialization).

---

## CellDesigner (`src/momapy/celldesigner/`)

### `src/momapy/celldesigner/__init__.py`
Re-exports: bases (`CellDesignerModelElement`, `CellDesignerNode`, `CellDesignerSingleHeadedArc`, `CellDesignerDoubleHeadedArc`, `CellDesignerLayout`, `CellDesignerMap`); modifications (`ModificationResidue`, `ModificationState`, `Modification`, `StructuralState`); regions (`Region`, `ModificationSite`, `CodingRegion`, `RegulatoryRegion`, `TranscriptionStartingSiteL`, `TranscriptionStartingSiteR`, `ProteinBindingDomain`); templates (`SpeciesTemplate`, `ProteinTemplate`, `GenericProteinTemplate`, `TruncatedProteinTemplate`, `ReceptorTemplate`, `IonChannelTemplate`, `GeneTemplate`, `RNATemplate`, `AntisenseRNATemplate`); compartment + species (`Compartment`, `Species`, `Protein`, `GenericProtein`, `TruncatedProtein`, `Receptor`, `IonChannel`, `Gene`, `RNA`, `AntisenseRNA`, `Phenotype`, `Ion`, `SimpleMolecule`, `Drug`, `Unknown`, `Complex`, `Degraded`); reaction participants (`Reactant`, `Product`); boolean logic (`BooleanLogicGateInput`, `BooleanLogicGate`, `AndGate`, `OrGate`, `NotGate`, `UnknownGate`); modulators (`KnownOrUnknownModulator`, `Modulator`, `UnknownModulator`, `Inhibitor`, `PhysicalStimulator`, `Catalyzer`, `Trigger`, `UnknownCatalyzer`, `UnknownInhibitor`); reactions (`Reaction`, `StateTransition`, `KnownTransitionOmitted`, `UnknownTransition`, `Transcription`, `Translation`, `Transport`, `HeterodimerAssociation`, `Dissociation`, `Truncation`); modulations (`KnownOrUnknownModulation`, `Modulation`, `Catalysis`, `Inhibition`, `PhysicalStimulation`, `Triggering`, `PositiveInfluence`, `NegativeInfluence`, `UnknownModulation`, `UnknownCatalysis`, `UnknownInhibition`, `UnknownPositiveInfluence`, `UnknownNegativeInfluence`, `UnknownPhysicalStimulation`, `UnknownTriggering`); `CellDesignerModel`; plus 50+ layout classes.

### `src/momapy/celldesigner/elements.py`
Purpose: base classes for CellDesigner layout and model.

- `CellDesignerModelElement(ModelElement)` — abstract base.
- `CellDesignerNode(SBGNNode)` — base for all CellDesigner nodes.
- `CellDesignerSingleHeadedArc(SingleHeadedArc)` — `arrowhead_*`, `path_*` styling; `own_drawing_elements()`.
- `CellDesignerDoubleHeadedArc(DoubleHeadedArc)` — `path_*` styling; `own_drawing_elements()`.
- `_SimpleNodeMixin(_SimpleMixin)`, `_MultiNodeMixin(_MultiMixin)` — drawing mixins; `_n` property.

### `src/momapy/celldesigner/model.py`
Purpose: CellDesigner model classes.

- **Regions**: `Region(CellDesignerModelElement)` (`name`, `active=False`) → `ModificationSite`, `CodingRegion`, `RegulatoryRegion`, `TranscriptionStartingSiteL`, `TranscriptionStartingSiteR`, `ProteinBindingDomain`.
- **Modifications**: `ModificationResidue` (`name`, `order`); `ModificationState(Enum)` — 13 values (PHOSPHORYLATED, ACETYLATED, UBIQUITINATED, …); `Modification`; `StructuralState` (`value`).
- **Templates**: `SpeciesTemplate(CellDesignerModelElement)` (`name`) → `ProteinTemplate` (`modification_residues`) → `GenericProteinTemplate`, `TruncatedProteinTemplate`, `ReceptorTemplate`, `IonChannelTemplate`; `GeneTemplate` (`regions`), `RNATemplate` (`regions`), `AntisenseRNATemplate` (`regions`).
- **Compartment / species**: `Compartment(SBMLCompartment, CellDesignerModelElement)`; `Species(SBMLSpecies, CellDesignerModelElement)` (`hypothetical`, `active`, `homomultimer`); `Protein` (`template`, `modifications`, `structural_states`) → `GenericProtein`, `TruncatedProtein`, `Receptor`, `IonChannel`; `Gene`, `RNA`, `AntisenseRNA` (each with `template`, `modifications`); `Phenotype`, `Ion`, `SimpleMolecule`, `Drug`, `Unknown`, `Degraded`; `Complex` (`structural_states`, `subunits`).
- **Reaction participants**: `Reactant(SpeciesReference, CellDesignerModelElement)` (`base`), `Product(SpeciesReference, CellDesignerModelElement)` (`base`).
- **Boolean logic**: `BooleanLogicGateInput` (`element: Species`); `BooleanLogicGate` (`inputs`) → `AndGate`, `OrGate`, `NotGate`, `UnknownGate`.
- **Modulators**: `KnownOrUnknownModulator(ModifierSpeciesReference, CellDesignerModelElement)` (`referred_species: Species | BooleanLogicGate`) → `Modulator` → `Inhibitor`, `PhysicalStimulator` → `Catalyzer`, also `Trigger`, `UnknownCatalyzer`, `UnknownInhibitor`; separate branch `UnknownModulator`.
- **Reactions**: `Reaction(SBMLReaction, CellDesignerModelElement)` (`reactants`, `products`, `modifiers`) → `StateTransition`, `KnownTransitionOmitted`, `UnknownTransition`, `Transcription`, `Translation`, `Transport`, `HeterodimerAssociation`, `Dissociation`, `Truncation`.
- **Modulations**: `KnownOrUnknownModulation` (`source`, `target`) → `Modulation` → `Catalysis`, `Inhibition`, `PhysicalStimulation`, `Triggering`, `PositiveInfluence`, `NegativeInfluence`; `UnknownModulation` → `UnknownCatalysis`, `UnknownInhibition`, `UnknownPositiveInfluence`, `UnknownNegativeInfluence`, `UnknownPhysicalStimulation`, `UnknownTriggering`.
- **Model**: `CellDesignerModel(SBMLModel)` — `species_templates`, `boolean_logic_gates`, `modulations`; `is_submodel(other) -> bool`.

### `src/momapy/celldesigner/layout.py`
Purpose: CellDesigner layout classes.

- **Container**: `CellDesignerLayout(Layout)`.
- **Species layouts** (each with active variant, all `_MultiNodeMixin, CellDesignerNode`): `GenericProteinLayout`, `IonChannelLayout`, `ComplexLayout`, `SimpleMoleculeLayout`, `IonLayout`, `UnknownLayout`, `DegradedLayout`, `GeneLayout`, `PhenotypeLayout`, `RNALayout`, `AntisenseRNALayout`, `TruncatedProteinLayout`, `ReceptorLayout`, `DrugLayout`.
- **Compartments**: `OvalCompartmentLayout`, `RectangleCompartmentLayout`, `CornerCompartmentLayout`, `LineCompartmentLayout`; enums `CompartmentCorner`, `CompartmentSide`.
- **Modifications & states**: `StructuralStateLayout`, `ModificationLayout`.
- **Arcs**: `CellDesignerSingleHeadedArc` subclasses (`ConsumptionLayout`, `ProductionLayout`, modulation arcs `CatalysisLayout`/`UnknownCatalysisLayout`, `InhibitionLayout`/`UnknownInhibitionLayout`, `PhysicalStimulationLayout`/`UnknownPhysicalStimulationLayout`, `ModulationLayout`/`UnknownModulationLayout`, `PositiveInfluenceLayout`/`UnknownPositiveInfluenceLayout`, `TriggeringLayout`/`UnknownTriggeringLayout`); `CellDesignerDoubleHeadedArc`; `ReactionLayout` subclasses (`StateTransitionLayout`, `KnownTransitionOmittedLayout`, `UnknownTransitionLayout`, `TranscriptionLayout`, `TranslationLayout`, `TransportLayout`, `HeterodimerAssociationLayout`, `DissociationLayout`, `TruncationLayout`); `LogicArcLayout`.
- **Logic gates**: `AndGateLayout`, `OrGateLayout`, `NotGateLayout`, `UnknownGateLayout`.

### `src/momapy/celldesigner/map.py`
- `CellDesignerMap(Map)` — `model: CellDesignerModel | None`, `layout: CellDesignerLayout | None`.

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

### `src/momapy/celldesigner/io/celldesigner/reader.py`
- `CellDesignerReadingContext(ReadingContext)` — adds `cd_compartments`, `cd_compartment_aliases`, `cd_species_templates`, `cd_species_aliases`, `cd_reactions`, `cd_modulations`, plus `real_model_source_ids` / `real_layout_source_ids` for split ID tracking.
- `CellDesignerReader(Reader)` — `read(file_path, return_type="map", with_model=True, with_layout=True, with_annotations=True, with_notes=True)`.
- Internal: `_KEY_TO_CLASS` (tuple keys → model/layout class pairs).

### `src/momapy/celldesigner/io/celldesigner/writer.py`
- `CellDesignerWritingContext(WritingContext)` — adds `subunit_to_complex`, `used_metaids`, `species_to_id`.
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
- `make_empty_layout(cd_element)`, `set_layout_size_and_position(reading_context, cd_model)`
- `make_segments(points)`, `make_points(cd_edit_points)`
- `make_species(reading_context, cd_species, ...)`, `make_species_modification(...)`, `make_species_structural_state(...)`
- `make_compartment_from_alias(reading_context, cd_compartment, cd_compartment_alias)`
- `make_segments_non_t_shape(reading_context, cd_reaction)`, `make_segments_left_t_shape(...)`, `make_segments_right_t_shape(...)`
- `make_reaction(reading_context, cd_reaction, ...)`
- `make_reactant_from_base(...)` / `make_reactant_from_link(...)`, `make_product_from_base(...)` / `make_product_from_link(...)`
- `make_modifier(reading_context, ...)`
- `make_logic_gate(reading_context, cd_element, layout_element_cls)`, `make_logic_arc(reading_context, gate_layout_element, input_layout_element)`
- `make_modulation(reading_context, ...)`
- Internal constants: `_LAYOUT_TO_ACTIVE_LAYOUT`, `_DEFAULT_FONT_FAMILY`, `_DEFAULT_FONT_SIZE`, `_DEFAULT_MODIFICATION_FONT_SIZE`, `_DEFAULT_FONT_FILL`.

### `src/momapy/celldesigner/io/celldesigner/_reading_parsing.py`
- `make_name(name: str|None) -> str|None` — handles CellDesigner name encoding.
- `make_id_to_element_mapping(cd_model) -> dict`
- `make_complex_alias_to_included_ids_mapping(cd_model) -> dict`
- XML traversal helpers: `get_annotation`, `get_extension`, `get_species`, `get_reactions`, `get_species_aliases`, `get_included_species_aliases`, `get_complex_species_aliases`, `get_compartments`, `get_compartment_aliases`, `get_protein_templates`, `get_gene_templates`, `get_rna_templates`, `get_antisense_rna_templates`, `get_notes`, `get_rdf`, `get_rdf_from_notes`, `get_width`, `get_height`, `get_bounds`, `get_edit_points_from_participant_link`, `get_edit_points_from_reaction`, etc.
- Constants: `_LINK_ANCHOR_POSITION_TO_ANCHOR_NAME`, `_TEXT_TO_CHARACTER` (special-character decoding table).

### `src/momapy/celldesigner/io/celldesigner/_writing.py`
- Geometry helpers: `_are_collinear(p1, p2, p3, epsilon=1e-6) -> bool`, `_is_degenerate_frame(origin, unit_x, unit_y, epsilon=1e-6) -> bool`, `_make_non_degenerate_frame(origin, unit_x, unit_y, epsilon=1e-6, scale=1.0) -> (Point, Point, Point)`.
- Encoding helpers: `color_to_cd_hex(color) -> str`, `encode_name(name) -> str`, `compute_cd_angle(...)`, `node_to_bounds_attrs(node) -> dict`.
- Reverse mapping constants: `_CD_NAMESPACE`, `_ANCHOR_NAME_TO_LINK_ANCHOR_POSITION`, `_CHARACTER_TO_TEXT`, `_CLASS_TO_CD_STRING`, `_CLASS_TO_REACTION_TYPE`, `_CLASS_TO_MODIFIER_TYPE`, `_MODIFICATION_STATE_TO_CD`.

---

## SBML (`src/momapy/sbml/`)

### `src/momapy/sbml/__init__.py`
Re-exports: `SBMLModelElement`, `BiomodelQualifier`, `BQBiol`, `BQModel`, `Compartment`, `ModifierSpeciesReference`, `RDFAnnotation`, `Reaction`, `SBML`, `SBMLModel`, `SimpleSpeciesReference`, `Species`, `SpeciesReference`.

### `src/momapy/sbml/elements.py`
- `SBMLModelElement(ModelElement)` — abstract; `name: str | None`, `sbo_term: str | None`, `metaid: str | None` (`compare=False, hash=False`). **(Formerly named `SBase`; renamed so that `Model` is never a `ModelElement` — see `tests/test_io_mappings.py`.)**

### `src/momapy/sbml/model.py`
Purpose: concrete SBML model classes and BioModels qualifier enums.

- **Qualifiers**: `BiomodelQualifier(Enum)` (abstract); `BQModel(BiomodelQualifier)` (HAS_INSTANCE, IS, IS_DERIVED_FROM, IS_DESCRIBED_BY, IS_INSTANCE_OF); `BQBiol(BiomodelQualifier)` (ENCODES, HAS_PART, HAS_PROPERTY, HAS_VERSION, IS, IS_DESCRIBED_BY, IS_ENCODED_BY, IS_HOMOLOG_TO, IS_PART_OF, IS_PROPERTY_OF, IS_VERSION_OF, OCCURS_IN, HAS_TAXON).
- **Annotation**: `RDFAnnotation` — plain frozen dataclass (metadata, not a model element); `qualifier`, `resources: frozenset[str]`.
- **Structure**: `Compartment(SBMLModelElement)` — `outside: Compartment | None`; `Species(SBMLModelElement)` — `compartment: Compartment | None`; `SimpleSpeciesReference(SBMLModelElement)` — `referred_species: Species`; `ModifierSpeciesReference(SimpleSpeciesReference)`; `SpeciesReference(SimpleSpeciesReference)` — `stoichiometry: float | None`; `Reaction(SBMLModelElement)` — `reversible`, `compartment`, `reactants`, `products`, `modifiers`.
- **Model**: `SBMLModel(Model)` — **does NOT inherit `SBMLModelElement`**; declares its own `name`, `sbo_term`, `metaid`, plus `compartments`, `species`, `reactions`. `is_submodel(other) -> bool`.
- **Root**: `SBML(SBMLModelElement)` — `xmlns`, `level=3`, `version=2`, `model: SBMLModel | None`.

### `src/momapy/sbml/io/sbml/reader.py`
- `ReadingContext` — `sbml_model`, `model`, `sbml_id_to_model_element`, `sbml_id_to_sbml_element`, `element_to_annotations`, `element_to_notes`, `map_element_to_ids`, `with_annotations`, `with_notes`.
- `SBMLReader(Reader)` — `check_file(file_path) -> bool`, `read(file_path, with_annotations=True, with_notes=True) -> ReaderResult`.

### `src/momapy/sbml/io/sbml/_model.py` (`make_*`)
- `make_annotations(rdf) -> list[RDFAnnotation]`, `make_notes(notes_element) -> list[str]`
- `make_annotations_from_element(sbml_element)`, `make_notes_from_element(sbml_element)`
- `make_empty_model(sbml_element)`
- `make_compartment(sbml_compartment, model)`
- `make_species(sbml_species, model, sbml_id_to_model_element)`
- `make_reaction(sbml_reaction, model)`
- `make_species_reference(sbml_species_reference, model, sbml_id_to_model_element)`
- `make_modifier_species_reference(sbml_modifier_species_reference, model, sbml_id_to_model_element)`

### `src/momapy/sbml/io/sbml/_parsing.py`
- `_RDF_NAMESPACE` constant.
- `get_prefix_and_name(tag)`, `get_description(rdf)`, `get_bags(bq_element)`, `get_list_items(bag)`
- `get_annotation(sbml_element)`, `get_species(sbml_model)`, `get_reactions(sbml_model)`, `get_compartments(sbml_model)`, `get_reactants(sbml_reaction)`, `get_products(sbml_reaction)`, `get_modifiers(sbml_reaction)`, `get_notes(sbml_element)`, `get_rdf(sbml_element)`
- `make_id_to_element_mapping(sbml_model) -> dict`

### `src/momapy/sbml/io/sbml/_qualifiers.py`
- `QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE` — `BQBiol | BQModel` → `(namespace_url, local_name)` (18 entries).
- `QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER` — reverse (19 entries; biology-qualifiers/hasInstance maps to `BQModel.HAS_INSTANCE`).

---

## Cross-cutting reminders

- **Frozen dataclasses everywhere**: mutate only via builders (`builder_from_object` → change → `build()`).
- **`Model` is a `MapElement`, never a `ModelElement`** in any format. `model.descendants()` traverses the `Model` directly by field walking, and the `Model` itself is excluded from its own element set.
- **Equality on elements**: structural (all fields except `id_`, `metaid`); dedup during read relies on it.
- **I/O `make_*` functions** are the public contract of `_reading_*` / `_writing_*` modules despite the underscore filenames.
- **ReaderResult public dicts**: `id_to_element`, `source_id_to_model_element`, `source_id_to_layout_element` — the SBGN and CellDesigner readers populate both `source_id_to_*` dicts; the split ensures alias ids appear only on the layout side and SBML ids only on the model side for CellDesigner (via `real_model_source_ids` / `real_layout_source_ids` in `build_id_mappings`).
