## Учебно-методический комплекс
***
```python
dependencies = "PyQt6 + web-engine, pyinstaller"
```
* Приложение разработано в рамках дипломного проекта
***
Чтобы проверить его работу, вам нужно:
1. Клонировать любым удобным способом
2. Далее запустить терминал в папке с исходным кодом проекта
3. ```commandline
   python -m venv env
   pip install -r requirements.txt
   ```
4. ```commandline
   mkrir compile
   cd compile
   pyinstqller -w -D -i "..\display\origin_files\icon.ico" --add-data "..\files;files" ..\main.py
   ```
5. Достать из папки ```compile\dist``` папку ```\main``` например на рабочий стол