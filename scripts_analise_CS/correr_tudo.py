# Corre todos os scripts pela ordem em que foram usados na análise.
# Uso: na pasta scripts_analise_CS, executar  python correr_tudo.py
import subprocess, sys

ORDEM = [
    'f0_auxiliares',                                   # Fase 0 – ficheiros auxiliares
    'f1a', 'f1b', 'f1c',                               # Fase 1A
    'f1d', 'f1e',                                      # Fase 1B
    'f2',                                              # Fase 2 – nível
    'f3',                                              # Fase 3 – setor
    'f4',                                              # Fase 4 – região
    'f5',                                              # Fase 5 – volume
    'f6a', 'f6',                                       # Fase 6 – GO
    'f7',                                              # Fase 7 – ocupação
    'f8a', 'f8', 'f8b0', 'f8b', 'f8c', 'f8d', 'f8e', 'f8f', 'f8g',  # Fase 8 – pessoal
    'f9a0', 'f9a', 'f9b',                              # Fase 9A – contexto municipal
    'f9c',                                             # Fase 9B – contexto regional
    'insp9c', 'f9d',                                   # Fase 9C – nacional, população
    'insp9d', 'f9e',                                   # Fase 9D – nacional, saúde
    'f10', 'f11', 'f12',                               # Síntese
    'fxl',                                             # Excel final
]

for s in ORDEM:
    print(f'--- {s}.py')
    r = subprocess.run([sys.executable, s + '.py'], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr)
        sys.exit(f'Erro em {s}.py – a execução parou.')
print('Concluído. Saídas de cálculo e figuras em w/; Excel na pasta principal.')
