# Rosetta API guide

State Library Victoria uses Rosetta as it digital asset management and preservation system. Rosetta makes data available via a series of REST API endpoints, the documentation for which is here: [https://developers.exlibrisgroup.com/rosetta/apis/rest-apis/](https://developers.exlibrisgroup.com/rosetta/apis/rest-apis/)

The [rosetta.py](./rosetta.py) script contained in this repo was developed as part of an investigation into using the API to support some SIP specific reporting requirements. However, it can be extended to explore any of the API endpoints documented.

## Authorisation

Authorisation to the API is via a basic authorisation header in the following format:

```bash
{user}-institutionCode-{institution_code}:{password}
```

For security reasons in [rosetta.py](./rosetta.py) the values for `user` and `password` are referred to from environmental variables. These values should be retrieved from whoever administers Rosetta. At State Library Victoria `institution_code` will vary according to which environment is being queried (see list below).

### Institution codes

#### Sandbox

- INS00 - Sandbox Default Institution
- INS002 - Sandbox Digital Original Material
- INS003 - Sandbox National Edeposit Collection
- TRN - Sandbox Created SLV material

#### Production

- INS00 - State Library Victoria Default Institution
- SLV - State Library Victoria Created Material
- SLVA - State Library Victoria Archived Material
- SLVDOM - State Library Victoria Digital Original Material