create view verbose_path as
  select path.id as kukan_id, path.start as kukan_kiten, ki.name as kiten_mei, path.end as kukan_syuten, syu.name as syuten_mei, path.length as kukan_kyori
  from path
  join station ki
    on path.start = ki.id
  join station syu
    on path.end = syu.id;