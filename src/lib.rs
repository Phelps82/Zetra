use pyo3::prelude::*;

/// Gols esperados com base no ataque do time e na defesa do adversário.
#[pyfunction]
fn gols_esperados(ataque: f64, defesa_adversaria: f64) -> f64 {
    (ataque / defesa_adversaria) * 1.3
}

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(gols_esperados, m)?)?;
    Ok(())
}
