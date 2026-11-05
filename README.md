# Zetra

Réplica do Brasfoot para o projeto de Estatística e Probabilidade.

- **Python**: probabilidade, estatística e gráficos (numpy, scipy, pandas, matplotlib).
- **Rust**: lógica de jogabilidade e simulação, exposta ao Python como módulo nativo via [PyO3](https://pyo3.rs).
- **Ferramentas**: [uv](https://docs.astral.sh/uv/) gerencia o lado Python e [maturin](https://www.maturin.rs/) compila o Rust e o instala no ambiente.

O restante da aplicação (interface, etc.) pode ser feito em outra linguagem e conversar com este módulo.

## Estrutura

```
Zetra/
├── Cargo.toml            # configuração do crate Rust
├── pyproject.toml        # configuração do projeto Python (build backend: maturin)
└── src/
    ├── lib.rs            # código Rust (módulo nativo `zetra._core`)
    └── zetra/
        ├── __init__.py   # código Python; reexporta o que vem do Rust
        ├── _core.pyi     # tipos do módulo Rust (para editor e type checker)
        └── py.typed
```

## Pré-requisitos (Arch Linux)

```fish
sudo pacman -S uv rustup
rustup default stable
```

## Criando o projeto do zero

```fish
uv init --lib --build-backend maturin --name zetra Zetra
cd Zetra

uv add numpy scipy pandas matplotlib
uv add --dev maturin pytest
```

## Compilar e testar

```fish
uv run maturin develop --uv
uv run python -c "import zetra; print(zetra.gols_esperados(80, 70))"
```

Resultado esperado: `1.4857142857142858`.

## Fluxo do dia a dia

| O que mudou | O que fazer |
|---|---|
| Código **Python** (`src/zetra/*.py`) | nada, vale na hora |
| Código **Rust** (`src/lib.rs`) | `uv run maturin develop --uv` |
| Testar desempenho de verdade | `uv run maturin develop --uv --release` |

## Adicionando uma função Rust acessível pelo Python

O `lib.rs` e o `__init__.py` precisam concordar sobre os nomes exportados pelo `_core`. Para cada função nova:

1. Escreva a função em `src/lib.rs` com `#[pyfunction]`.
2. Registre no `#[pymodule]` com `m.add_function(wrap_pyfunction!(nome, m)?)?;`.
3. Importe em `src/zetra/__init__.py` e inclua em `__all__`.
4. Declare a assinatura em `src/zetra/_core.pyi`.
5. Recompile com `uv run maturin develop --uv`.

Exemplo (`src/lib.rs`):

```rust
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
```

`src/zetra/__init__.py`:

```python
from zetra._core import gols_esperados

__all__ = ["gols_esperados"]
```

`src/zetra/_core.pyi`:

```python
def gols_esperados(ataque: float, defesa_adversaria: float) -> float: ...
```

## Problemas comuns

- **`ModuleNotFoundError: No module named '...'`**: o nome do módulo Python é o nome do projeto (`zetra`), não outro.
- **`ImportError: cannot import name '...' from 'zetra._core'`**: o `__init__.py` pede um nome que o Rust não exporta (ou o Rust não foi recompilado). Confira o `lib.rs`, o `__init__.py` e rode `uv run maturin develop --uv`.
- **`grep --include=*.rs` falha no fish**: o fish tenta expandir o `*`. Use aspas (`--include='*.rs'`) ou `rg "padrao" -g '*.rs'`.

## Arquitetura prevista

- **Rust**: loop de jogabilidade, simulação de partidas, estado do campeonato.
- **Python**: distribuições de probabilidade (por exemplo, Poisson para gols), estatísticas, gráficos e, se necessário, uma API (FastAPI) para o restante da aplicação.
- Fluxo preferido: **Python chama Rust**, passando os dados como argumentos. Chamar Python de dentro do Rust é possível com PyO3, mas complica o build.
- Alternativa, se o restante da aplicação ficar em outra linguagem: dois processos separados conversando por HTTP/JSON.
