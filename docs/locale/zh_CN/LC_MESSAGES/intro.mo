��    �      <              \  d   ]  2   �  �   �  �   �	     �
  <   �
  z   �
  {   V  t   �    G  �   I  �   �    �  m   �  8   +  =   d  v   �  C     �   ]  �   	    �         -  V   G  }   �  p     `   �  T   �  X   C  @   �  +   �  6   	  
   @     K     X  B   n  t   �  ;   &     b  Q   �  .  �  _     �   c  <     -   W  U   �  o   �     K  �   d  &   &  f   M     �  x   �     =  �   U  7   �  �   0   a   �   I   !  G   c!  6   �!  �   �!  -   t"  �   �"  
   B#  )   M#     w#     �#  n   �#  3   $     D$     L$  +   Y$     �$     �$  -   �$  �   �$     l%  4   �%     �%  `   �%  *   2&     ]&     {&  0   �&  �   �&  U   Q'  A   �'  �   �'  �   �(  f   2)  B   �)  -   �)  r   
*  �   }*    +  >   ,  X   P,  �   �,  (   /-  m   X-  =   �-  &   .  G   +.  O   s.  ^   �.  1   "/  ;   T/  z   �/  U   0  �   a0  2   �0  4   1  J   T1  1   �1  O   �1  �   !2  j   �2  O   3  z   b3  �   �3  >   w4  2   �4  4   �4  %   5     D5  y   I5  D   �5  ?   6  7   H6  "   �6  �  �6  Y   &8  *   �8  �   �8  �   @9     :  3   :  u   B:  |   �:  z   5;  �   �;  �   s<  �   =    �=  R   �>  %   H?  /   n?  {   �?  4   @  �   O@  �   �@    �A     �B  .  C  ?   CD  m   �D  l   �D  \   ^E  I   �E  K   F  -   QF  !   F  9   �F     �F     �F     �F  6   G  e   >G  9   �G     �G  L   �G    IH  `   aI  �   �I  -   tJ  !   �J  H   �J  n   K     |K  �   �K  <   UL  U   �L     �L  o   �L     nM  �   �M  >    N  �   _N  k   �N  E   ^O  C   �O  5   �O  �   P     �P  �   �P     GQ  #   PQ     tQ     �Q  H   �Q  4   �Q     R     $R  -   1R     _R     lR  *   �R  �   �R     FS  +   fS     �S  \   �S  .   T     1T     OT  *   _T  �   �T  B   U  3   XU  �   �U  ~   .V  E   �V  /   �V     #W  e   BW  h   �W  �   X  =   �X  Z   Y  �   lY  *   �Y  c   Z  3   �Z  /   �Z  B   �Z  E   )[  `   o[  3   �[  B   \  p   G\  L   �\  c   ]  -   i]  -   �]  B   �]  3   ^  V   <^  �   �^  ^   #_  G   �_  �   �_  �   M`  <   �`  4   "a  /   Wa  )   �a     �a  x   �a  >   1b  ;   pb  &   �b     �b   "input" or "output" indicates whether IoDef of TableAttrDef is from input or output of ComponentDef. "input" or "output". The same as selected columns. **Attribute Groups** are advanced usage in Component Attribute declaration. Only a small part of audiences may utilize this feature one day. You may check **Attribute Groups** later. **IndividualTable** is a table owned by one party, which means there is a single item in data_refs field of DistData. **IndividualTable** should be packed into **meta** field of DistData which includes **schema** and **line_count**. **NOTE** **Report** should be packed into **meta** field of DistData. **StorageConfig** specifies the storage root of a party. It could be a local file path, a database table or an OSS bucket. **Struct Attribute Group** : all children of the group need to fill-in together. e.g. "a/c/f", "a/d", "a/d/g" in the graph. **Union Attribute Group** : user must select one child of the group to fill-in. e.g. "a/c" and "a/d/h" in the graph. **VerticalTable** is a vertical partitioned table owned by multiple parties. **VerticalTable** contains multiple **schema**. Correspondingly, there should be multiple data_refs in DistData. **VerticalTable** should be packed into **meta** field of DistData. **Why Struct Attribute Group?** In most cases, Struct Attribute Groups are used with Union Attribute Groups to express a complicated attribute tree. **Why Union Attribute Group?** Attributes of a component is identical to a survey. Sometimes answer of a question may affect the following questions given to survey takers. Union Attribute Group is to descibe such cases. **Why only one uri for each output?** For each output, only one uri is provided. It will be used by all parties to generate all data_refs of this output DistData. It looks weird since we may give each party a different uri. However, this is not a good idea: *col_min_cnt_inclusive* and *col_max_cnt_inclusive* indicates how many columns should be selected for *name*. *desc* indicates what the selected columns for to users. *extra_attrs* are extra attributes for each selected columns. *name* is the name of columns, e.g. "label", "key", "features". It should unique among all TableAttrDefs of one input. A **AttributeDef** represents a node of a component attribute tree. A **DataRef** is a pointer to a single file belongs to one party. **uri** is the relative path to storage root of its owner. **DataRef** is public and open to all parties. A Distdata may contain multliple pieces of private data. Each piece of private data is referred by a DataRef. DataRef is public in DistData. Don't put anything private in uri of DataRef since every party gets exactly the same DataRef. A Struct Attribute Group represent a bunch of attributes which should be filled together. e.g. "a/c/f/k" in graph is a struct attribute group with children "a/c/f/k/p" and "a/c/f/k/q". "a/c/f/k/p" and "a/c/f/k/q" are logically grouped together in this case and should be filled together. A Typical Attribute Tree A Union Attribute Group is similar to a Stuct Attribute group since it also has children. However, user should choose only one of children to fill-in. e.g. "a/d/h" is a union attribute group and "a/d/h/n" and "a/d/h/o" are children. User must choose "a/d/h/n" or "a/d/h/o" to fill. A component represent a piece of application which could be integrated into workflows. A group of a components could be organized by a **CompListDef**. Each privacy-preserving application must provide a CompList. A runtime instance of a component is called a Node. To evaluate a component of an apllication, you must provide: AT_BOOL And corresponding scalar list types. You may check [AttrType](spec.md#attrtype) as well. Afterwards, you should use **AtomicAttrDesc** to further describe Atomic Attributes. Again, you could leave **TableAttrDef** alone at this moment since it is unusual to use. At this moment, we don't have an official protocol for Workflow. At this moment, we only support *local_fs*. At this moment, we support the following scalar types: Attributes Column name. Common DistData Types Component is the most complicated protocol in OpenSecretflow Spec. DataRef only contains a uri. In order to retrieve the remote data, the owner has to utilize their own StorageConfig. Descriptions: Displays multiple read-only fields in groups. DistData consists of two parts: Div: A division or a section of a page, consists of Descriptions, Tables or Divs. Don't confused with data partitioning in Database systems. In such systems, dividing a large dataset into several small partitions placed on different machines is quite common. However, there are no owner enforcements on partitions, which means which machine is selected to place a partition is random. Don't try to store any secret with uris. You need to protect the files pointed by uris instead. Each party has the full control of the storage root and they could move the files afterwards. We hope to keep our system simple and don't invest any effort in file system management. Extra attributes. The rules are the same as Attribute nodes. Fill-ining TableAttrDef is quite complicated. First, you should answer the selected columns. The attr_path consists of three parts: For **Atomic Attributes**, first you should indicate with "type" field in [AttributeDef](spec.md#attributedef). For all atomic attribue: For any attribute, you may use **prefixes** to indicate all ancestors of the attribute tree node. The prefixes for root attributes is an empty list. e.g. Prefixed of "a/d/h" is ["a", "d", "h"]. For float, int, float list, int float: For input data, **SystemInfo** describes the application and environment which could consume the data. For lists only: For union attribute group, you must provide a pair of attr_path and attr to indicate your choice of children explicitly. How to Evaluate a Node? If **types** of an IoDef is *sf.table.individual* and/or *sf.table.vertical*. You may further indicates columns of table to use in apllications with TableAttrDef. If is_optional is true, default_value must be provided. If you choose children named e, the attr is a [Attribute](spec.md#attribute) with *s* field is e, i.e. children selection is a string. If you choose children named f, the attr is a [Attribute](spec.md#attribute) with *s* field is f. In SecretFlow, the type str for IndividualTable is *sf.table.individual*. In SecretFlow, the type str for IndividualTable is *sf.table.vertical*. In SecretFlow, the type str for Report is *sf.report*. In privacy-preserving applications, a data is "distributed" since it is owned by multiple parties like MPC models or vertical-partitioned tables. Introduction to SecretFlow Open Specification IoDef is to specify the requirement of an input or output of the component. You should use **types** to declare accepted types of [DistData](spec.md#distdata). IoDef name IoDef name. The same as selected columns. It contains output DistData. It contains: Let's go through **Atomic Attributes**, **Struct Attribute Group** and **Union Attribute Group** respectively. NodeEvalParam, all fields required by ComponentDef. Outputs Private data Private data, which is accessible to owner. Public data Public data includes: Public data, which is acesssible to everyone. Report is another common DistData which is totally public and doesn't own any data_ref. We use a **Report** to reveal statistic outputs in most cases. Report related protos are: Report: The top-level of a report, consists of Tabs. Retrieve Remote Data StorageConfig, you must provide it to let application to get the remote data pointed by DataRef. Tab: A page of a report, consists of Divs. Table: Displays rows of data. TableAttrDef name TableAttrDef name. The same as selected columns. The attr_path is *(input|output)/(IoDef name)/(TableAttrDef name)(/(column name)(/(extra attributes))?)?* for select columns and extra attributes. The attr_path of an atmoic attribute is the full path of an attribute tree node. e.g. The child of an Attribute Group could be another Attribute Group. The leaves of the tree are called **Atomic Attributes**, which represent solid fields for users to fill-in e.g. bucket size or learning rate. e.g. "a/b", "a/c/e/i", "a/c/f/j" in the graph. The length of attr_paths and attrs must be the same. They should obey the same order. e.g. if the n-th attr is the value of n-th attr_path. The non-leaf nodes of the tree are called **Attribute Group**. There are two kind of Attribute Groups: The result is expressed with  **NodeEvalResult** from application. The specification is subject to modification. Then, if TableAttrDef contains *extra_attrs*, you should continue to answer it. The attr_path contains five parts: To define a Struct Attribute Group, you should indicate with "type" field in [AttributeDef](spec.md#attributedef) with AT_STRUCT_GROUP. To define a Union Attribute Group, you should indicate with "type" field in [AttributeDef](spec.md#attributedef) with AT_UNION_GROUP. Afterwards, you should use [UnionAttrGroupDesc](spec.md#attributedefunionattrgroupdesc) to specify the default selection of children. Use is_optional to indicate if a user answer must be provided. Use list_min_length_inclusive and list_max_length_inclusive to limit the length of list. Use lower_bound_enabled/upper_bound_enabled, lower_bound/upper_bound, lower_bound_inclusive/upper_bound_inclusive to limit the value. We copied the same attribute tree above. We introduce [DistData](spec.md#distdata) to represent inputs and outputs in privacy-preserving applications. We organize all attributes of a component as attribute trees. We purpose some common DistData types. We use attr_paths and attrs to answer attributes defined in components. When we have multiple parties, the list of output uris would be extremely long. With a tuple of domain, name and version, user could locate a unqiue component in your system. You could use ComponentDef to define a component: You don't need fill-in anything for Struct Attribute Group. You should provide an uri relative to StorageConfig for each config. The order should be the same defined in ComponentDef. You should use *ss* field of [Attribute](spec.md#attribute) to list selected columns. [Attribute](spec.md#attribute) is used to express the value of an attribute. Please use *is_na* to indicate the value is *n/a* explicitly. attr_path of attribute node named *j* is "a/c/f/j" attr_path of attribute node named *q* is "a/c/f/k/q" attr_paths, attrs: Attributes of the component. Will be discussed further. attributes. Please check AttributeDef part below. domain, name, version: to locate a component from the comp list of application. domain: namespace of component. You could use this field to group components. e.g. In SecretFlow, we have 'ml.train', 'feature', etc. e.g. A typical attr_path for extra_attrs of a selected columns is "input/train_dataset/features/x_1/a/b/c" e.g. A typical attr_path for selected columns id "input/train_dataset/features" e.g. This [link](https://github.com/secretflow/secretflow/blob/main/docker/comp_list.json) is the comp list of secretflow. e.g. We may ask users to provide a table as an input/output, then select some columns as features, and fillin other attributes for each selected columns. e.g. for union attribute group named c, the attr_path is "a/c" inputs and outputs. Please check IoDef part below. inputs: Inputs of the component, should be DistData. meta, anything else should be public. name name: should be unique among the domain. However you could have components with the same name while in different domains. output_uris: Output uris for each output. Will be discussed further. type, instructs privacy-preserving applications to process data types indicates type restrictions for selected columns. version: the version of component. Project-Id-Version: Open Secretflow 
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2023-09-29 15:43+0800
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language: zh_CN
Language-Team: zh_CN <LL@li.org>
Plural-Forms: nplurals=1; plural=0;
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.12.1
 "input"或"output"表示TableAttrDef的IoDef是来自组件定义的输入还是输出。 "input"或"output"。与所选列相同。 属性组 是组件属性声明中的高级用法。只有一小部分用户可能会在某一天使用此功能。您可以稍后查看属性组。 IndividualTable是由一方拥有的表格，这意味着DistData的data_refs字段中只有一个项。IndividualTable应该打包到DistData的meta字段中，该字段包括schema和line_count。 注意 Report应该被打包到DistData的meta字段中。 StorageConfig指定了一方的存储根目录。它可以是本地文件路径、数据库表格或 OSS 存储桶。 **Struct Attribute Group** ：组内的所有子节点都需要一起填写。例如，在图中"a/c/f"，"a/d"，"a/d/g"。 **Union Attribute Group** ：用户必须选择组内的一个子节点进行填写。例如，在图中"a/c"和"a/d/h"。 VerticalTable 是多个方拥有的垂直分区表。VerticalTable 包含多个schema。相应地，DistData中应该有多个data_refs。VerticalTable 应该打包到DistData的meta字段中。 为什么需要 Struct Attribute Group ？ 在大多数情况下，Struct Attribute Group 与 Union Attribute Group 一起用于表示复杂的属性树。 为什么需要 Union Attribute Group ？ 组件的属性类似于调查问卷。有时问题的答案可能会影响给调查对象提出的后续问题。Union Attribute Group 用于描述这种情况。 **为什么每个输出只有一个URI？** 对于每个输出，只提供一个URI。它将由所有参与方用于生成该输出DistData的所有data_ref。这看起来很奇怪，因为我们可能会给每个参与方一个不同的URI。然而，这不是一个好主意： col_min_cnt_inclusive和col_max_cnt_inclusive指示应选择多少列作为name。 desc指示用户所选列的含义。 extra_attrs是每个选定列的额外属性。 name是列的名称，例如"label"、"key"、"features"。它应该在一个输入的所有TableAttrDefs中是唯一的。 AttributeDef 表示组件属性树的一个节点。 DataRef是指向一个属于一方的单个文件的指针。uri是相对于其所有者的存储根目录的路径。DataRef是公开的，所有方都可以访问。 DistData可能包含多个私有数据片段。每个私有数据片段由DataRef引用。DataRef是DistData中的公共字段，不要在DataRef的uri中放置任何私有信息，因为每个方都获得完全相同的DataRef。 Struct Attribute Group 代表一组应该一起填写的属性。例如，在图中"a/c/f/k" 是一个 Struct Attribute Group ，它的子节点是 "a/c/f/k/p" 和 "a/c/f/k/q"。在这种情况下，"a/c/f/k/p" 和 "a/c/f/k/q" 是逻辑上一起分组的，并且应该一起填写。 一棵典型的属性树 Union Attribute Group 与 Stuct Attribute group 类似，因为它们都有子节点。然而，用户只能选择一个子节点进行填写。例如，"a/d/h" 是一个 Union Attribute Group ，它的子节点是 "a/d/h/n" 和 "a/d/h/o"。用户必须选择 "a/d/h/n" 或者 "a/d/h/o" 进行填写。 组件表示可以集成到工作流中的一份应用程序。 一组组件可以通过CompListDef进行组织。每个隐私保护应用程序必须提供一个CompList。 组件的运行时实例称为节点。要评估一个应用程序的组件，您必须提供以下内容： AT_BOOL 和相应的标量列表类型。您也可以查看 [AttrType](spec.md#attrtype) 。 之后，您应该使用 AtomicAttrDesc 来进一步描述原子属性。 同样，您可以暂时不用担心TableAttrDef，因为它很少使用。 目前我们没有官方的工作流协议。 目前我们只支持 local_fs。 在目前的版本中，我们支持以下标量类型： 属性 列名称。 常见的DistData类型 Component是隐语开放标准中最复杂的协议。 DataRef只包含一个uri。为了获取远程数据，所有者必须使用自己的StorageConfig。 Descriptions：以组的形式显示多个只读字段。 DistData包含两个部分： Div：页面的一个部分或节，由Descriptions、Tables或Divs组成。 不要将其与数据库系统中的数据分区搞混了。在这种系统中，将大型数据集划分为放置在不同机器上的几个小分区是很常见的。但是，对分区没有所有者的强制执行，这意味着选择哪个机器来放置分区是随机的。 不要试图将任何机密信息存储在uri中。你应该保护的是由uri指向的文件。 每个参与方都完全控制存储根目录，并且他们之后可以移动文件。我们希望保持我们的系统简单，不在文件系统管理上投入任何精力。 额外属性。规则与属性节点相同。 填写TableAttrDef非常复杂。 首先，您应该回答选择的列。attr_path由三个部分组成： 对于原子属性，首先需要在 [AttributeDef](spec.md#attributedef) 中使用"type"字段进行指定。 对于所有的原子属性： 对于任何属性，您可以使用 **prefixes** 来指示属性树节点的所有祖先。根属性的前缀列表为空列表。例如，"a/d/h"的 **prefixes** 是["a", "d", "h"]。 对于浮点数、整数、浮点数列表和整数列表： 对于输入数据，SystemInfo描述了可能使用数据的应用程序和环境。 仅适用于列表： 对于 union attribute group ，您必须提供一对attr_path和attr，以明确指示您选择的子节点。 如何评估一个节点？ 如果IoDef的types是sf.table.individual和/或sf.table.vertical，您可以使用TableAttrDef进一步指示在应用程序中使用的表的列。 如果 is_optional 为 true，则必须提供 default_value。 如果您选择名为e的子元素，则attr是一个[Attribute](spec.md#attribute) ，其中s字段为e，即子元素选择是一个字符串。 如果您选择名为f的子元素，则attr是一个[Attribute](spec.md#attribute) ，其中s字段为f。 在SecretFlow中，IndividualTable的类型为 sf.table.individual。 在SecretFlow中，IndividualTable的类型为 sf.table.vertical。 在SecretFlow中，Report的类型为 *sf.report* 。 在隐私保护应用程序中，一个数据可能是"分布式"，因为它由多方拥有，例如MPC模型或者垂直分区的表格。 隐语开放标准介绍 IoDef用于指定组件的输入或输出要求。您应该使用types来声明接受的 [DistData](spec.md#distdata) 的类型。 IoDef名 IoDef名称。与所选列相同。 它包含输出的DistData。 它包含： 让我们分别介绍原子属性、结构属性组和联合属性组。 NodeEvalParam，ComponentDef所需的所有字段。 输出 私有数据 私有数据，只有所有者可以访问。 公共数据 公共数据包括： 公共数据，每个人都可以访问。 Report 是另一个常见的DistData，它完全公开，并且不拥有任何data_ref。我们使用Report来展示大多数情况下的统计输出。 与报告相关的 proto 是： Report：报告的顶级，由Tabs组成。 获取远程数据 StorageConfig，您必须提供它以让应用程序获取由DataRef指定的远程数据。 Tab：报告的一个页面，由Divs组成。 Table：显示数据的行。 TableAttrDef名 TableAttrDef名称。与所选列相同。 attr_path是 *(input|output)/(IoDef name)/(TableAttrDef name)(/(column name)(/(extra attributes))?)?* ，用于选择列和额外属性。 原子属性的attr_path是属性树节点的完整路径。例如 属性组的子节点可以是另一个属性组。 树的叶子节点称为原子属性，表示用户需要填写的固定字段，例如桶大小或学习率，在图中表示为"a/b"，"a/c/e/i"，"a/c/f/j"。 attr_paths和attrs的长度必须相同。它们应该遵守相同的顺序。例如，第n个attr是第n个attr_path的值。 树的非叶子节点称为属性组。有两种类型的属性组： 结果由应用程序的NodeEvalResult表示。 本标准可能会有修改。 然后，如果TableAttrDef包含extra_attrs，则应继续回答它。attr_path包含五个部分： 要定义一个Struct Attribute Group ，在AttributeDef中使用"type"字段指定为AT_STRUCT_GROUP。 定义一个 Union Attribute Group ，您需要在AttributeDef的"type"字段中使用AT_UNION_GROUP进行指示。然后，您可以使用UnionAttrGroupDesc来指定子属性的默认选择。 使用 is_optional 来指示是否必须提供用户答案。 使用 list_min_length_inclusive 和 list_max_length_inclusive 来限制列表的长度。 使用 lower_bound_enabled/upper_bound_enabled，lower_bound/upper_bound，lower_bound_inclusive/upper_bound_inclusive 来限制值。 我们复制了上面相同的属性树。 我们引入了 [DistData](spec.md#distdata) 来表示隐私保护应用程序中的输入和输出 我们将组件的所有属性组织成属性树。 我们提供了一些常见的DistData类型。 我们使用attr_paths和attrs来回答组件中定义的属性。 当我们有多个参与方时，输出URI列表会变得非常长。 通过域、名称和版本的组合，用户可以在系统中定位到一个唯一的组件。 你可以使用ComponentDef来定义一个组件： 对于 Struct Attribute Group ，您不需要填写任何内容。 您应该为每个配置提供相对于StorageConfig的uri。顺序应与ComponentDef中定义的顺序相同。 您应该使用 [Attribute](spec.md#attribute) 的ss字段列出所选列。 [Attribute](spec.md#attribute) 用于表示属性的值。请使用is_na来明确表示值为n/a。 属性节点名为j的attr_path是"a/c/f/k/j" 属性节点名为q的attr_path是"a/c/f/k/q" attr_paths，attrs：组件的属性。稍后将进一步讨论。 attributes: 请查看下面的AttributeDef部分。 domain，name，version：用于从应用程序的组件列表中定位一个组件。 domain: 组件的命名空间。可以使用此字段对组件进行分组。例如，在SecretFlow中，我们有 'ml.train'，'feature'等。 例如，选择列的额外属性的典型attr_path为"input/train_dataset/features/x_1/a/b/c" 例如，选择列id的典型attr_path为"input/train_dataset/features" 例如，这个 [链接](https://github.com/secretflow/secretflow/blob/main/docker/comp_list.json) 是secretflow的组件列表。 例如，我们可能要求用户提供一个表作为输入/输出，然后选择某些列作为特征，并为每个选定的列填写其他属性。 例如，对于名为c的联合属性组，attr_path是"a/c" inputs 和 outputs: 请查看下面的IoDef部分。 inputs：组件的输入，类型是DistData。 meta ，任何其他可以公共的数据 名称 name: 在命名空间中必须是唯一的。但是，在不同的命名空间中，可以具有相同名称的组件。 output_uris：每个输出的URI。稍后将进一步讨论。 type ，指导隐私保护应用程序处理数据的方式 types指示所选列的类型限制。 version: 组件的版本。 