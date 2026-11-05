# Zetra

Réplica do Brasfoot para o projeto de Estatística e Probabilidade.

- **Python**: probabilidade, estatística e gráficos (numpy, scipy, pandas, matplotlib).
- **Rust**: lógica de jogabilidade e simulação, exposta ao Python como módulo nativo.
- **Ferramentas**: [uv](https://docs.astral.sh/uv/) gerencia o Python e as dependências, e o [maturin](https://www.maturin.rs/) compila o Rust e o instala no ambiente.

Este guia explica como instalar e rodar o projeto em **Ubuntu** e em **Windows**.

## 1. Instalar os pré-requisitos

Você precisa de: **Git**, **uv**, **Rust** (via rustup) e um **compilador C/C++** (o Rust usa o linker do sistema).

### Ubuntu

```bash
sudo apt update
sudo apt install -y build-essential curl git

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Feche e abra o terminal de novo (ou rode `source ~/.bashrc`) para o `uv` e o `cargo` entrarem no PATH.

### Windows (PowerShell)

```powershell
winget install --id Git.Git -e
winget install --id astral-sh.uv -e
winget install --id Rustlang.Rustup -e
winget install --id Microsoft.VisualStudio.2022.BuildTools -e
```

Ao instalar o **Build Tools**, abra o *Visual Studio Installer* e marque a carga de trabalho **"Desenvolvimento para desktop com C++"**. Sem ela o Rust não consegue compilar. Depois, **feche e abra o PowerShell** e rode:

```powershell
rustup default stable
```

### Conferir a instalação (Ubuntu e Windows)

```
git --version
uv --version
rustc --version
cargo --version
```

Os quatro comandos devem mostrar uma versão.

## 2. Baixar e preparar o projeto

```
git clone <URL-DO-REPOSITORIO> Zetra
cd Zetra
uv sync
```

O `uv sync` cria o ambiente virtual (`.venv`), instala as dependências Python e **compila o Rust**. Na primeira vez pode demorar alguns minutos.

## 3. Rodar

```
uv run python -c "import zetra; print(zetra.gols_esperados(80, 70))"
```

Resultado esperado: `1.4857142857142858`.

Use sempre `uv run ...` para executar scripts. Assim você não precisa ativar o ambiente virtual manualmente, e o comando é o mesmo no Ubuntu e no Windows.

## Estrutura do projeto

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

## Desenvolvimento

| O que mudou | O que fazer |
|---|---|
| Código **Python** (`src/zetra/*.py`) | nada, vale na hora |
| Código **Rust** (`src/lib.rs`) | `uv run maturin develop --uv` |
| Testar desempenho de verdade | `uv run maturin develop --uv --release` |
| Adicionou uma dependência Python | `uv add nome-do-pacote` |
| Rodar os testes | `uv run pytest` |

### Adicionando uma função Rust acessível pelo Python

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

| Sintoma | Causa e solução |
|---|---|
| `uv: command not found` / `cargo: command not found` | O PATH ainda não foi atualizado. Feche e abra o terminal. |
| **Windows:** `linker 'link.exe' not found` | Falta o C++ do Build Tools. Reabra o *Visual Studio Installer* e marque "Desenvolvimento para desktop com C++". |
| **Ubuntu:** `linker 'cc' not found` | Rode `sudo apt install build-essential`. |
| `ModuleNotFoundError: No module named 'zetra'` | Rode `uv sync` dentro da pasta do projeto e use `uv run python ...`. |
| `ImportError: cannot import name '...' from 'zetra._core'` | O `__init__.py` pede um nome que o Rust não exporta, ou o Rust não foi recompilado. Confira o `lib.rs` e rode `uv run maturin develop --uv`. |
| **Windows:** erro de permissão ao rodar scripts do PowerShell | Rode `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. |

## Arquitetura prevista

- **Rust**: loop de jogabilidade, simulação de partidas, estado do campeonato.
- **Python**: distribuições de probabilidade (por exemplo, Poisson para gols), estatísticas, gráficos e, se necessário, uma API (FastAPI) para o restante da aplicação.
- Fluxo preferido: **Python chama Rust**, passando os dados como argumentos.
- Se o restante da aplicação ficar em outra linguagem, a comunicação pode ser por HTTP/JSON entre processos separados.
