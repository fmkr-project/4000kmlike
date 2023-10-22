-- Reset views
drop view if exists v_path;
drop view if exists v_path_no_transfer;
drop view if exists v_transfer;

-- List paths with station names instead of IDs
create view if not exists v_path as
  select
    path.id as kukan_id,
	path.start as kukan_kiten,
	ki.name as kiten_mei,
	path.length as kukan_kyori,
	case when path.onfootonly = '1' then "True" else "False" end as norikae,
	case when path.road = '1' then "True" else "False" end as douro,
	path.end as kukan_syuten,
	syu.name as syuten_mei
  from path
  join station ki
    on path.start = ki.id
  join station syu
    on path.end = syu.id;

-- List non-transfer paths
create view v_path_no_transfer as
  select
    kukan_id,
	kukan_kiten,
	kiten_mei,
	kukan_kyori,
	case when douro = "True" then "bus" else "rail" end as syurui,
	kukan_syuten,
	syuten_mei
  from v_path
  where norikae = "False"
  order by syurui desc, kukan_id;
 
-- Only list transfers
create view v_transfer as
  select
	kukan_id,
	kukan_kiten,
	kiten_mei,
	kukan_syuten,
	syuten_mei
  from v_path
  where norikae = "True";