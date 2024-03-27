# SecretFlow Open Specification
> This page is auto-generated with protoc-gen-doc.

## Table of Contents


 ### [DATA](#DATA)



  - Messages
      - [DistData](#distdata)
      - [DistData.DataRef](#distdatadataref)
      - [IndividualTable](#individualtable)
      - [StorageConfig](#storageconfig)
      - [StorageConfig.LocalFSConfig](#storageconfiglocalfsconfig)
      - [SystemInfo](#systeminfo)
      - [TableSchema](#tableschema)
      - [VerticalTable](#verticaltable)





 ### [COMPONENT](#COMPONENT)



  - Messages
      - [Attribute](#attribute)
      - [AttributeDef](#attributedef)
      - [AttributeDef.AtomicAttrDesc](#attributedefatomicattrdesc)
      - [AttributeDef.UnionAttrGroupDesc](#attributedefunionattrgroupdesc)
      - [CompListDef](#complistdef)
      - [ComponentDef](#componentdef)
      - [IoDef](#iodef)
      - [IoDef.TableAttrDef](#iodeftableattrdef)



  - Enums
      - [AttrType](#attrtype)




 ### [EVALUATION](#EVALUATION)



  - Messages
      - [NodeEvalParam](#nodeevalparam)
      - [NodeEvalResult](#nodeevalresult)





 ### [REPORT](#REPORT)



  - Messages
      - [Descriptions](#descriptions)
      - [Descriptions.Item](#descriptionsitem)
      - [Div](#div)
      - [Div.Child](#divchild)
      - [Report](#report)
      - [Tab](#tab)
      - [Table](#table)
      - [Table.HeaderItem](#tableheaderitem)
      - [Table.Row](#tablerow)






(DATA)=
 ## DATA

Proto file: [secretflow/spec/v1/data.proto](https://github.com/secretflow/spec/tree/main/secretflow/spec/v1/data.proto)


 <!-- end services -->

### Messages


(distdata)=
#### DistData
A public record for a general distributed data.

The type of this distributed data, should be meaningful to components.

The concrete data format (include public and private parts) is defined by
other protos.

Suggested internal types, i.e.
- sf.table.vertical_table      represent a secretflow vertical table
- sf.table.individual_table      represent a secretflow individual table


| Field | Type | Description |
| ----- | ---- | ----------- |
| name | [ string](#string) | The name of this distributed data. |
| type | [ string](#string) | Type. |
| system_info | [ SystemInfo](#systeminfo) | Describe the system information that used to generate this distributed data. |
| meta | [ google.protobuf.Any](#googleprotobufany) | Public information, known to all parties. i.e. VerticalTable. |
| data_refs | [repeated DistData.DataRef](#distdatadataref) | Remote data references. |
 <!-- end Fields -->
 <!-- end HasFields -->


(distdatadataref)=
#### DistData.DataRef
A reference to a data that is stored in the remote path.


| Field | Type | Description |
| ----- | ---- | ----------- |
| uri | [ string](#string) | The path information relative to StorageConfig of the party. |
| party | [ string](#string) | The owner party. |
| format | [ string](#string) | The storage format, i.e. csv. |
 <!-- end Fields -->
 <!-- end HasFields -->


(individualtable)=
#### IndividualTable
IndividualTable describes a table owned by a single party.


| Field | Type | Description |
| ----- | ---- | ----------- |
| schema | [ TableSchema](#tableschema) | Schema. |
| line_count | [ int64](#int64) | If -1, the number is unknown. |
 <!-- end Fields -->
 <!-- end HasFields -->


(storageconfig)=
#### StorageConfig
A StorageConfig specifies the root for all data for one party.
- At this moment, only local_fs is supported
- We would support OSS, databases in future.


| Field | Type | Description |
| ----- | ---- | ----------- |
| type | [ string](#string) | Supported: local_fs. |
| local_fs | [ StorageConfig.LocalFSConfig](#storageconfiglocalfsconfig) | local_fs config. |
 <!-- end Fields -->
 <!-- end HasFields -->


(storageconfiglocalfsconfig)=
#### StorageConfig.LocalFSConfig
For local_fs.


| Field | Type | Description |
| ----- | ---- | ----------- |
| wd | [ string](#string) | Working directory. |
 <!-- end Fields -->
 <!-- end HasFields -->


(systeminfo)=
#### SystemInfo
Describe the application related to data.


| Field | Type | Description |
| ----- | ---- | ----------- |
| app | [ string](#string) | The application name. Supported: `secretflow` |
| app_meta | [ google.protobuf.Any](#googleprotobufany) | Meta for application. |
 <!-- end Fields -->
 <!-- end HasFields -->


(tableschema)=
#### TableSchema
The schema of a table.
- A col must be one of `id | feature | label`. By default, it should be a
feature.
- All names must match the regexp `[A-Za-z0-9.][A-Za-z0-9_>./]*`.
- All data type must be one of
* int8
* int16
* int32
* int64
* uint8
* uint16
* uint32
* uint64
* float16
* float32
* float64
* bool
* int
* float
* str


| Field | Type | Description |
| ----- | ---- | ----------- |
| ids | [repeated string](#string) | Id column name(s). Optional, can be empty. |
| features | [repeated string](#string) | Feature column name(s). |
| labels | [repeated string](#string) | Label column name(s). Optional, can be empty. |
| id_types | [repeated string](#string) | Id column data type(s). Len(id) should match len(id_types). |
| feature_types | [repeated string](#string) | Feature column data type(s). Len(features) should match len(feature_types). |
| label_types | [repeated string](#string) | Label column data type(s). Len(labels) should match len(label_types). |
 <!-- end Fields -->
 <!-- end HasFields -->


(verticaltable)=
#### VerticalTable
VerticalTable describes a virtual vertical partitioning table from multiple
parties.


| Field | Type | Description |
| ----- | ---- | ----------- |
| schemas | [repeated TableSchema](#tableschema) | The vertical partitioned slices' schema. Must match data_refs in the parent DistData message. |
| line_count | [ int64](#int64) | If -1, the number is unknown. |
 <!-- end Fields -->
 <!-- end HasFields -->
 <!-- end messages -->

### Enums
 <!-- end Enums -->

(COMPONENT)=
 ## COMPONENT

Proto file: [secretflow/spec/v1/component.proto](https://github.com/secretflow/spec/tree/main/secretflow/spec/v1/component.proto)


 <!-- end services -->

### Messages


(attribute)=
#### Attribute
The value of an attribute


| Field | Type | Description |
| ----- | ---- | ----------- |
| f | [ float](#float) | FLOAT |
| i64 | [ int64](#int64) | INT NOTE(junfeng): "is" is preserved by Python. Replaced with "i64". |
| s | [ string](#string) | STRING |
| b | [ bool](#bool) | BOOL |
| fs | [repeated float](#float) | FLOATS |
| i64s | [repeated int64](#int64) | INTS |
| ss | [repeated string](#string) | STRINGS |
| bs | [repeated bool](#bool) | BOOLS |
| is_na | [ bool](#bool) | Indicates the value is missing explicitly. |
 <!-- end Fields -->
 <!-- end HasFields -->


(attributedef)=
#### AttributeDef
Describe an attribute.


| Field | Type | Description |
| ----- | ---- | ----------- |
| prefixes | [repeated string](#string) | Indicates the ancestors of a node, e.g. `[name_a, name_b, name_c]` means the path prefixes of current Attribute is `name_a/name_b/name_c/`. Only `^[a-zA-Z0-9_.-]*$` is allowed. `input` and `output` are reserved. |
| name | [ string](#string) | Must be unique in the same level just like Linux file systems. Only `^[a-zA-Z0-9_.-]*$` is allowed. `input` and `output` are reserved. |
| desc | [ string](#string) | none |
| type | [ AttrType](#attrtype) | none |
| atomic | [ AttributeDef.AtomicAttrDesc](#attributedefatomicattrdesc) | none |
| union | [ AttributeDef.UnionAttrGroupDesc](#attributedefunionattrgroupdesc) | none |
| custom_protobuf_cls | [ string](#string) | Extras for custom protobuf attribute |
 <!-- end Fields -->
 <!-- end HasFields -->


(attributedefatomicattrdesc)=
#### AttributeDef.AtomicAttrDesc
Extras for an atomic attribute.
Including: `AT_FLOAT | AT_INT | AT_STRING | AT_BOOL | AT_FLOATS | AT_INTS |
AT_STRINGS | AT_BOOLS`.


| Field | Type | Description |
| ----- | ---- | ----------- |
| list_min_length_inclusive | [ int64](#int64) | Only valid when type is `AT_FLOATS \| AT_INTS \| AT_STRINGS \| AT_BOOLS`. |
| list_max_length_inclusive | [ int64](#int64) | Only valid when type is `AT_FLOATS \| AT_INTS \| AT_STRINGS \| AT_BOOLS`. |
| is_optional | [ bool](#bool) | If True, when Atmoic Attr is not provided or is_na, default_value would be used. Else, Atmoic Attr must be provided. |
| default_value | [ Attribute](#attribute) | A reasonable default for this attribute if the user does not supply a value. |
| allowed_values | [ Attribute](#attribute) | Only valid when type is `AT_FLOAT \| AT_INT \| AT_STRING \| AT_FLOATS \| AT_INTS \| AT_STRINGS`. Please use list fields of AtomicParameter, i.e. `ss`, `i64s`, `fs`. If the attribute is a list, allowed_values is applied to each element. |
| lower_bound_enabled | [ bool](#bool) | Only valid when type is `AT_FLOAT \| AT_INT \| AT_FLOATS \| AT_INTS `. If the attribute is a list, lower_bound is applied to each element. |
| lower_bound | [ Attribute](#attribute) | none |
| lower_bound_inclusive | [ bool](#bool) | none |
| upper_bound_enabled | [ bool](#bool) | Only valid when type is `AT_FLOAT \| AT_INT \| AT_FLOATS \| AT_INTS `. If the attribute is a list, upper_bound is applied to each element. |
| upper_bound | [ Attribute](#attribute) | none |
| upper_bound_inclusive | [ bool](#bool) | none |
 <!-- end Fields -->
 <!-- end HasFields -->


(attributedefunionattrgroupdesc)=
#### AttributeDef.UnionAttrGroupDesc
Extras for a union attribute group.


| Field | Type | Description |
| ----- | ---- | ----------- |
| default_selection | [ string](#string) | The default selected child. |
 <!-- end Fields -->
 <!-- end HasFields -->


(complistdef)=
#### CompListDef
A list of components


| Field | Type | Description |
| ----- | ---- | ----------- |
| name | [ string](#string) | none |
| desc | [ string](#string) | none |
| version | [ string](#string) | none |
| comps | [repeated ComponentDef](#componentdef) | none |
 <!-- end Fields -->
 <!-- end HasFields -->


(componentdef)=
#### ComponentDef
The definition of a comp.


| Field | Type | Description |
| ----- | ---- | ----------- |
| domain | [ string](#string) | Namespace of the comp. |
| name | [ string](#string) | Should be unique among all comps of the same domain. |
| desc | [ string](#string) | none |
| version | [ string](#string) | Version of the comp. |
| attrs | [repeated AttributeDef](#attributedef) | none |
| inputs | [repeated IoDef](#iodef) | none |
| outputs | [repeated IoDef](#iodef) | none |
 <!-- end Fields -->
 <!-- end HasFields -->


(iodef)=
#### IoDef
Define an input/output for component.


| Field | Type | Description |
| ----- | ---- | ----------- |
| name | [ string](#string) | should be unique among all IOs of the component. |
| desc | [ string](#string) | none |
| types | [repeated string](#string) | Must be one of DistData.type in data.proto |
| attrs | [repeated IoDef.TableAttrDef](#iodeftableattrdef) | Only valid for tables. The attribute path for a TableAttrDef is `{input\|output}/{IoDef name}/{TableAttrDef name}`. |
 <!-- end Fields -->
 <!-- end HasFields -->


(iodeftableattrdef)=
#### IoDef.TableAttrDef
An extra attribute for a table.

If provided in a IoDef, e.g.
```json
{
  "name": "feature",
  "types": [
      "int",
      "float"
  ],
  "col_min_cnt_inclusive": 1,
  "col_max_cnt": 3,
  "attrs": [
      {
          "name": "bucket_size",
          "type": "AT_INT"
      }
  ]
}
```
means after a user provide a table as IO, they should also specify
cols as "feature":
- col_min_cnt_inclusive is 1: At least 1 col to be selected.
- col_max_cnt_inclusive is 3: At most 3 cols to be selected.
And afterwards, user have to fill an int attribute called bucket_size for
each selected cols.


| Field | Type | Description |
| ----- | ---- | ----------- |
| name | [ string](#string) | Must be unique among all attributes for the table. |
| desc | [ string](#string) | none |
| types | [repeated string](#string) | Accepted col data types. Please check comments of TableSchema in data.proto. |
| col_min_cnt_inclusive | [ int64](#int64) | inclusive |
| col_max_cnt_inclusive | [ int64](#int64) | none |
| extra_attrs | [repeated AttributeDef](#attributedef) | extra attribute for specified col. |
 <!-- end Fields -->
 <!-- end HasFields -->
 <!-- end messages -->

### Enums


(attrtype)=
#### AttrType
Supported attribute types.

| Name | Number | Description |
| ---- | ------ | ----------- |
| ATTR_TYPE_UNSPECIFIED | 0 | none |
| AT_FLOAT | 1 | FLOAT |
| AT_INT | 2 | INT |
| AT_STRING | 3 | STRING |
| AT_BOOL | 4 | BOOL |
| AT_FLOATS | 5 | FLOATS |
| AT_INTS | 6 | INTS |
| AT_STRINGS | 7 | STRINGS |
| AT_BOOLS | 8 | BOOLS |
| AT_STRUCT_GROUP | 9 | none |
| AT_UNION_GROUP | 10 | none |
| AT_SF_TABLE_COL | 11 | none |
| AT_CUSTOM_PROTOBUF | 12 | none |


 <!-- end Enums -->

(EVALUATION)=
 ## EVALUATION

Proto file: [secretflow/spec/v1/evaluation.proto](https://github.com/secretflow/spec/tree/main/secretflow/spec/v1/evaluation.proto)


 <!-- end services -->

### Messages


(nodeevalparam)=
#### NodeEvalParam
Evaluate a node.
- CompListDef + StorageConfig + NodeEvalParam + other extra configs ->
NodeEvalResult

NodeEvalParam contains all the information to evaluate a component.


| Field | Type | Description |
| ----- | ---- | ----------- |
| domain | [ string](#string) | Domain of the component. |
| name | [ string](#string) | Name of the component. |
| version | [ string](#string) | Version of the component. |
| attr_paths | [repeated string](#string) | The path of attributes. The attribute path for a TableAttrDef is `(input\|output)/(IoDef name)/(TableAttrDef name)(/(column name)(/(extra attributes))?)?`. |
| attrs | [repeated Attribute](#attribute) | The value of the attribute. Must match attr_paths. |
| inputs | [repeated DistData](#distdata) | The input data, the order of inputs must match inputs in ComponentDef. NOTE: Names of DistData doesn't need to match those of inputs in ComponentDef definition. |
| output_uris | [repeated string](#string) | The output data uris, the order of output_uris must match outputs in ComponentDef. |
 <!-- end Fields -->
 <!-- end HasFields -->


(nodeevalresult)=
#### NodeEvalResult
NodeEvalResult contains outputs of a component evaluation.


| Field | Type | Description |
| ----- | ---- | ----------- |
| outputs | [repeated DistData](#distdata) | Output data. |
 <!-- end Fields -->
 <!-- end HasFields -->
 <!-- end messages -->

### Enums
 <!-- end Enums -->

(REPORT)=
 ## REPORT

Proto file: [secretflow/spec/v1/report.proto](https://github.com/secretflow/spec/tree/main/secretflow/spec/v1/report.proto)


 <!-- end services -->

### Messages


(descriptions)=
#### Descriptions
Displays multiple read-only fields in groups.


| Field | Type | Description |
| ----- | ---- | ----------- |
| name | [ string](#string) | Name of the Descriptions. |
| desc | [ string](#string) | none |
| items | [repeated Descriptions.Item](#descriptionsitem) | none |
 <!-- end Fields -->
 <!-- end HasFields -->


(descriptionsitem)=
#### Descriptions.Item



| Field | Type | Description |
| ----- | ---- | ----------- |
| name | [ string](#string) | Name of the field. |
| desc | [ string](#string) | none |
| type | [ string](#string) | Must be one of bool/int/float/str |
| value | [ Attribute](#attribute) | none |
 <!-- end Fields -->
 <!-- end HasFields -->


(div)=
#### Div
A division or a section of a page.


| Field | Type | Description |
| ----- | ---- | ----------- |
| name | [ string](#string) | Name of the Div. |
| desc | [ string](#string) | none |
| children | [repeated Div.Child](#divchild) | none |
 <!-- end Fields -->
 <!-- end HasFields -->


(divchild)=
#### Div.Child



| Field | Type | Description |
| ----- | ---- | ----------- |
| type | [ string](#string) | Supported: descriptions, table, div. |
| descriptions | [ Descriptions](#descriptions) | none |
| table | [ Table](#table) | none |
| div | [ Div](#div) | none |
 <!-- end Fields -->
 <!-- end HasFields -->


(report)=
#### Report



| Field | Type | Description |
| ----- | ---- | ----------- |
| name | [ string](#string) | Name of the Report. |
| desc | [ string](#string) | none |
| tabs | [repeated Tab](#tab) | none |
| err_code | [ int32](#int32) | none |
| err_detail | [ string](#string) | Structed error detail (JSON encoded message). |
 <!-- end Fields -->
 <!-- end HasFields -->


(tab)=
#### Tab
A page of a report.


| Field | Type | Description |
| ----- | ---- | ----------- |
| name | [ string](#string) | Name of the Tab. |
| desc | [ string](#string) | none |
| divs | [repeated Div](#div) | none |
 <!-- end Fields -->
 <!-- end HasFields -->


(table)=
#### Table
Displays rows of data.


| Field | Type | Description |
| ----- | ---- | ----------- |
| name | [ string](#string) | Name of the Table. |
| desc | [ string](#string) | none |
| headers | [repeated Table.HeaderItem](#tableheaderitem) | none |
| rows | [repeated Table.Row](#tablerow) | none |
 <!-- end Fields -->
 <!-- end HasFields -->


(tableheaderitem)=
#### Table.HeaderItem



| Field | Type | Description |
| ----- | ---- | ----------- |
| name | [ string](#string) | none |
| desc | [ string](#string) | none |
| type | [ string](#string) | Must be one of bool/int/float/str |
 <!-- end Fields -->
 <!-- end HasFields -->


(tablerow)=
#### Table.Row



| Field | Type | Description |
| ----- | ---- | ----------- |
| name | [ string](#string) | none |
| desc | [ string](#string) | none |
| items | [repeated Attribute](#attribute) | none |
 <!-- end Fields -->
 <!-- end HasFields -->
 <!-- end messages -->

### Enums
 <!-- end Enums -->
 <!-- end Files -->

## Scalar Value Types

| Type | Notes | C++ Type | Java Type | Python Type |
| ---- | ----- | -------- | --------- | ----------- |
| <div><h4 id="double" /></div><a name="double" /> double |  | double | double | float |
| <div><h4 id="float" /></div><a name="float" /> float |  | float | float | float |
| <div><h4 id="int32" /></div><a name="int32" /> int32 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint32 instead. | int32 | int | int |
| <div><h4 id="int64" /></div><a name="int64" /> int64 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint64 instead. | int64 | long | int/long |
| <div><h4 id="uint32" /></div><a name="uint32" /> uint32 | Uses variable-length encoding. | uint32 | int | int/long |
| <div><h4 id="uint64" /></div><a name="uint64" /> uint64 | Uses variable-length encoding. | uint64 | long | int/long |
| <div><h4 id="sint32" /></div><a name="sint32" /> sint32 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int32s. | int32 | int | int |
| <div><h4 id="sint64" /></div><a name="sint64" /> sint64 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int64s. | int64 | long | int/long |
| <div><h4 id="fixed32" /></div><a name="fixed32" /> fixed32 | Always four bytes. More efficient than uint32 if values are often greater than 2^28. | uint32 | int | int |
| <div><h4 id="fixed64" /></div><a name="fixed64" /> fixed64 | Always eight bytes. More efficient than uint64 if values are often greater than 2^56. | uint64 | long | int/long |
| <div><h4 id="sfixed32" /></div><a name="sfixed32" /> sfixed32 | Always four bytes. | int32 | int | int |
| <div><h4 id="sfixed64" /></div><a name="sfixed64" /> sfixed64 | Always eight bytes. | int64 | long | int/long |
| <div><h4 id="bool" /></div><a name="bool" /> bool |  | bool | boolean | boolean |
| <div><h4 id="string" /></div><a name="string" /> string | A string must always contain UTF-8 encoded or 7-bit ASCII text. | string | String | str/unicode |
| <div><h4 id="bytes" /></div><a name="bytes" /> bytes | May contain any arbitrary sequence of bytes. | string | ByteString | str |
