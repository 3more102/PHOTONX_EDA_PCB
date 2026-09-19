use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug)]
struct Aabb {
    min_x: f64,
    min_y: f64,
    max_x: f64,
    max_y: f64,
}

impl Aabb {
    fn new(min_x: f64, min_y: f64, max_x: f64, max_y: f64) -> Result<Self, String> {
        if ![min_x, min_y, max_x, max_y].into_iter().all(f64::is_finite) {
            return Err("AABB coordinates must be finite".to_string());
        }
        if min_x > max_x || min_y > max_y {
            return Err("AABB minimum must not exceed maximum".to_string());
        }
        Ok(Self {
            min_x,
            min_y,
            max_x,
            max_y,
        })
    }

    fn expanded(&self, distance: f64) -> Self {
        Self {
            min_x: self.min_x - distance,
            min_y: self.min_y - distance,
            max_x: self.max_x + distance,
            max_y: self.max_y + distance,
        }
    }

    fn intersects(&self, other: &Self) -> bool {
        !(self.max_x < other.min_x
            || other.max_x < self.min_x
            || self.max_y < other.min_y
            || other.max_y < self.min_y)
    }
}

#[derive(Clone, Debug)]
struct Entry {
    id: String,
    bounds: Aabb,
}

fn cell_index(value: f64, cell_size: f64) -> Result<i64, String> {
    let index = (value / cell_size).floor();
    if !index.is_finite() || index < i64::MIN as f64 || index > i64::MAX as f64 {
        return Err("AABB coordinate is outside the supported spatial-index range".to_string());
    }
    Ok(index as i64)
}

fn cell_bounds(bounds: &Aabb, cell_size: f64) -> Result<(i64, i64, i64, i64), String> {
    Ok((
        cell_index(bounds.min_x, cell_size)?,
        cell_index(bounds.min_y, cell_size)?,
        cell_index(bounds.max_x, cell_size)?,
        cell_index(bounds.max_y, cell_size)?,
    ))
}

fn candidate_pairs_core(
    boxes: Vec<(String, f64, f64, f64, f64)>,
    tolerance: f64,
    cell_size: f64,
) -> Result<Vec<(String, String)>, String> {
    if !cell_size.is_finite() || cell_size <= 0.0 {
        return Err("cell_size must be a positive finite value".to_string());
    }
    if !tolerance.is_finite() {
        return Err("tolerance must be finite".to_string());
    }

    let mut ids = BTreeSet::new();
    let mut entries = Vec::with_capacity(boxes.len());
    for (id, min_x, min_y, max_x, max_y) in boxes {
        if !ids.insert(id.clone()) {
            return Err(format!("duplicate spatial id: {id}"));
        }
        entries.push(Entry {
            id,
            bounds: Aabb::new(min_x, min_y, max_x, max_y)?,
        });
    }

    let mut cells: BTreeMap<(i64, i64), Vec<usize>> = BTreeMap::new();
    for (index, entry) in entries.iter().enumerate() {
        let (min_ix, min_iy, max_ix, max_iy) = cell_bounds(&entry.bounds, cell_size)?;
        for ix in min_ix..=max_ix {
            for iy in min_iy..=max_iy {
                cells.entry((ix, iy)).or_default().push(index);
            }
        }
    }

    let mut pairs: BTreeSet<(String, String)> = BTreeSet::new();
    for (index, entry) in entries.iter().enumerate() {
        let query = entry.bounds.expanded(tolerance);
        let (min_ix, min_iy, max_ix, max_iy) = cell_bounds(&query, cell_size)?;
        let mut candidates = BTreeSet::new();

        for ix in min_ix..=max_ix {
            for iy in min_iy..=max_iy {
                if let Some(cell_entries) = cells.get(&(ix, iy)) {
                    candidates.extend(cell_entries.iter().copied());
                }
            }
        }

        for other_index in candidates {
            if other_index == index {
                continue;
            }
            let other = &entries[other_index];
            if !query.intersects(&other.bounds) {
                continue;
            }

            let pair = if entry.id <= other.id {
                (entry.id.clone(), other.id.clone())
            } else {
                (other.id.clone(), entry.id.clone())
            };
            pairs.insert(pair);
        }
    }

    Ok(pairs.into_iter().collect())
}

#[cfg(feature = "python")]
mod python {
    use super::candidate_pairs_core;
    use pyo3::exceptions::PyValueError;
    use pyo3::prelude::*;

    #[pyfunction]
    fn candidate_pairs_aabb(
        boxes: Vec<(String, f64, f64, f64, f64)>,
        tolerance: f64,
        cell_size: f64,
    ) -> PyResult<Vec<(String, String)>> {
        candidate_pairs_core(boxes, tolerance, cell_size).map_err(PyValueError::new_err)
    }

    #[pymodule]
    fn _photonx_native(module: &Bound<'_, PyModule>) -> PyResult<()> {
        module.add_function(wrap_pyfunction!(candidate_pairs_aabb, module)?)?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::candidate_pairs_core;

    fn boxes() -> Vec<(String, f64, f64, f64, f64)> {
        vec![
            ("c".to_string(), 5.0, 5.0, 6.0, 6.0),
            ("a".to_string(), 0.0, 0.0, 1.0, 1.0),
            ("b".to_string(), 0.9, 0.9, 2.0, 2.0),
        ]
    }

    #[test]
    fn returns_deterministic_intersecting_pairs() {
        let pairs = candidate_pairs_core(boxes(), 0.0, 1.0).unwrap();
        assert_eq!(pairs, vec![("a".to_string(), "b".to_string())]);
    }

    #[test]
    fn tolerance_expands_queries() {
        let boxes = vec![
            ("a".to_string(), 0.0, 0.0, 0.2, 0.2),
            ("b".to_string(), 0.25, 0.0, 0.4, 0.2),
        ];
        assert!(candidate_pairs_core(boxes.clone(), 0.0, 1.0)
            .unwrap()
            .is_empty());
        assert_eq!(
            candidate_pairs_core(boxes, 0.1, 1.0).unwrap(),
            vec![("a".to_string(), "b".to_string())]
        );
    }

    #[test]
    fn duplicate_ids_fail_closed() {
        let boxes = vec![
            ("a".to_string(), 0.0, 0.0, 1.0, 1.0),
            ("a".to_string(), 2.0, 2.0, 3.0, 3.0),
        ];
        assert!(candidate_pairs_core(boxes, 0.0, 1.0)
            .unwrap_err()
            .contains("duplicate spatial id"));
    }

    #[test]
    fn invalid_cell_size_fails_closed() {
        assert!(candidate_pairs_core(boxes(), 0.0, 0.0).is_err());
    }
}
