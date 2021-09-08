import pytest

from pygnmi.path_generator import gnmi_path_generator
from pygnmi.spec.gnmi_pb2 import Path, PathElem

def compare_paths(actual: Path, expected: Path):
    assert expected.origin == actual.origin
    assert len(expected.elem) == len(actual.elem)

    for exp_elem, actual_elem in zip(expected.elem, actual.elem):
        assert exp_elem.name == actual_elem.name
        assert len(exp_elem.key) == len(actual_elem.key)
        for key in exp_elem.key:
            assert key in actual_elem.key
            assert exp_elem.key[key] == actual_elem.key[key]

test_paths = [
    # empty path, with & without an origin
    ("", None, Path(elem=[])),
    ("/", None, Path(elem=[])),
    ("", "rfc7951", Path(origin="rfc7951", elem=[])),
    ("/", "rfc7951", Path(origin="rfc7951", elem=[])),

    # some paths from examples/pure_python
    ("interfaces/interface[name=Management1]/state/counters",
     None,
     Path(elem=[PathElem(name="interfaces"),
                PathElem(name="interface",
                         key={"name": "Management1"}),
                PathElem(name="state"),
                PathElem(name="counters")])),

    ("/interfaces/interface[name=Management1]/state/counters",
     None,
     Path(elem=[PathElem(name="interfaces"),
                PathElem(name="interface",
                         key={"name": "Management1"}),
                PathElem(name="state"),
                PathElem(name="counters")])),

    ("openconfig-interfaces:interfaces/interface[name=Loopback1]",
     None,
     Path(origin="openconfig-interfaces",
          elem=[PathElem(name="interfaces"),
                PathElem(name="interface",
                         key={"name": "Loopback1"})])),

    ("/openconfig-interfaces:interfaces/interface[name=Loopback1]",
     None,
     Path(origin="openconfig-interfaces",
          elem=[PathElem(name="interfaces"),
                PathElem(name="interface",
                         key={"name": "Loopback1"})])),

    ("/openconfig-interfaces:interfaces/interface[name=Loopback1]",
     "",
     Path(elem=[PathElem(name="openconfig-interfaces:interfaces"),
                PathElem(name="interface",
                         key={"name": "Loopback1"})])),

    # Examples taken from https://www.rfc-editor.org/rfc/rfc8349.html
    # Note: intermediate elements with module names, and value with colons & slash;
    # container control-plane-protocol has key made of two elements
    ("ietf-routing:routing/"
     "control-plane-protocols/"
     "control-plane-protocol[type=ietf-routing:static][name=st0]/"
     "static-routes/"
     "ietf-ipv6-unicast-routing:ipv6/"
     "route[destination-prefix=::/0]",
     None,
     Path(origin="ietf-routing",
          elem=[PathElem(name="routing"),
                PathElem(name="control-plane-protocols"),
                PathElem(name="control-plane-protocol",
                         key={"type": "ietf-routing:static",
                              "name": "st0"}),
                PathElem(name="static-routes"),
                PathElem(name="ietf-ipv6-unicast-routing:ipv6"),
                PathElem(name="route",
                         key={"destination-prefix": "::/0"})])),

    # the same, explicitely giving the origin
    ("ietf-routing:routing/"
     "control-plane-protocols/"
     "control-plane-protocol[type=ietf-routing:static][name=st0]/"
     "static-routes/"
     "ietf-ipv6-unicast-routing:ipv6/"
     "route[destination-prefix=::/0]",
     "rfc7951",
     Path(origin="rfc7951",
          elem=[PathElem(name="ietf-routing:routing"),
                PathElem(name="control-plane-protocols"),
                PathElem(name="control-plane-protocol",
                         key={"type": "ietf-routing:static",
                              "name": "st0"}),
                PathElem(name="static-routes"),
                PathElem(name="ietf-ipv6-unicast-routing:ipv6"),
                PathElem(name="route",
                         key={"destination-prefix": "::/0"})])),

    # Taken from https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1610/b_1610_programmability_cg/gnmi_protocol.html#id_84819
    ("openconfig-interfaces:interfaces/interface[name=Loopback111]",
     "rfc7951",
     Path(origin="rfc7951",
          elem=[PathElem(name="openconfig-interfaces:interfaces"),
                PathElem(name="interface",
                         key={"name": "Loopback111"})])),

    ("/oc-if:interfaces/interface[name=Loopback111]",
     "legacy",
     Path(origin="legacy",
          elem=[PathElem(name="oc-if:interfaces"),
                PathElem(name="interface",
                         key={"name": "Loopback111"})])),

    # no origin
    ("interfaces/interface[name=Loopback111]",
     "",
     Path(elem=[PathElem(name="interfaces"),
                PathElem(name="interface",
                         key={"name": "Loopback111"})])),

]

@pytest.mark.parametrize("xpath, path_origin, yangpath", test_paths)
def test_xpath(xpath, path_origin, yangpath):
    compare_paths(gnmi_path_generator(xpath, path_origin), yangpath)
            
    
