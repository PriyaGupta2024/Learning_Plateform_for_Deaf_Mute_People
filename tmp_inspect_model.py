import zipfile, json
p='learning/sign_model.keras'
with zipfile.ZipFile(p) as z:
    cfg = json.loads(z.read('config.json').decode('utf-8'))
print('type_name', cfg.get('class_name'))
print('config keys', cfg.get('config', {}).keys())
print('config class_name', cfg['config'].get('class_name'))
print('layers count', len(cfg['config'].get('layers', [])))
for i,layer in enumerate(cfg['config'].get('layers', [])[:20]):
    print(i, layer['class_name'], layer['config'].get('name'), layer['config'].get('batch_input_shape'))
