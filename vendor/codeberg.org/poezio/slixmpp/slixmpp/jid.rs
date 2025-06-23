use pyo3::exceptions::{PyNotImplementedError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyString;

pyo3::create_exception!(slixmpp.jid, InvalidJID, PyValueError, "Raised when attempting to create a JID that does not pass validation.\n\nIt can also be raised if modifying an existing JID in such a way as\nto make it invalid, such trying to remove the domain from an existing\nfull JID while the local and resource portions still exist.");

fn to_exc(err: jid::Error) -> PyErr {
    InvalidJID::new_err(err.to_string())
}

/// A representation of a Jabber ID, or JID.
///
/// Each JID may have three components: a user, a domain, and an optional resource. For example:
/// user@domain/resource
///
/// When a resource is not used, the JID is called a bare JID. The JID is a full JID otherwise.
///
/// Raises InvalidJID if the parser rejects it.
#[pyclass(name = "JID", module = "slixmpp.jid")]
struct PyJid {
    jid: Option<jid::Jid>,
}

#[pymethods]
impl PyJid {
    #[new]
    #[pyo3(signature = (jid=None, bare=false))]
    fn new(jid: Option<&Bound<'_, PyAny>>, bare: bool) -> PyResult<Self> {
        if let Some(jid) = jid {
            if let Ok(py_jid) = jid.extract::<PyRef<PyJid>>() {
                if bare {
                    if let Some(jid) = &(*py_jid).jid {
                        Ok(PyJid {
                            jid: Some(jid.to_bare().into()),
                        })
                    } else {
                        Ok(PyJid { jid: None })
                    }
                } else {
                    Ok(PyJid {
                        jid: (*py_jid).jid.clone(),
                    })
                }
            } else {
                let jid: &str = jid.extract()?;
                if jid.is_empty() {
                    Ok(PyJid { jid: None })
                } else {
                    let mut jid = jid::Jid::new(jid).map_err(to_exc)?;
                    if bare {
                        jid = jid.into_bare().into()
                    }
                    Ok(PyJid { jid: Some(jid) })
                }
            }
        } else {
            Ok(PyJid { jid: None })
        }
    }

    /*
    // TODO: implement or remove from the API
    fn unescape() {
    }
    */

    #[getter]
    fn get_bare(&self) -> String {
        match &self.jid {
            None => String::new(),
            Some(jid) => jid.to_bare().to_string(),
        }
    }

    #[setter]
    fn set_bare(&mut self, bare: &str) -> PyResult<()> {
        let bare = jid::BareJid::new(bare).map_err(to_exc)?;
        self.jid = Some(match self.jid.as_ref().map(jid::Jid::try_as_full) {
            Some(Ok(full)) => bare.with_resource(full.resource()).into(),
            Some(Err(_)) | None => bare.into(),
        });
        Ok(())
    }

    #[getter]
    fn get_full(&self) -> String {
        match &self.jid {
            None => String::new(),
            Some(jid) => jid.to_string(),
        }
    }

    #[setter]
    fn set_full(&mut self, full: &str) -> PyResult<()> {
        // JID.full = 'domain' is acceptable in slixmpp.
        self.jid = Some(jid::Jid::new(full).map_err(to_exc)?);
        Ok(())
    }

    #[getter]
    fn get_node(&self) -> String {
        match &self.jid {
            None => String::new(),
            Some(jid) => jid
                .node()
                .map(ToString::to_string)
                .unwrap_or_else(String::new),
        }
    }

    #[setter]
    fn set_node(&mut self, node: Option<&str>) -> PyResult<()> {
        if let Some(node) = node {
            let node = jid::NodePart::new(node).map_err(to_exc)?;
            self.jid = Some(match self.jid.as_ref().map(jid::Jid::try_as_full) {
                Some(Ok(full)) => jid::FullJid::from_parts(
                    Some(&node),
                    full.domain(),
                    full.resource(),
                ).into(),
                Some(Err(bare)) => {
                    jid::BareJid::from_parts(Some(&node), bare.domain()).into()
                }
                None => Err(InvalidJID::new_err("JID.node must apply to a proper JID"))?,
            });
        } else {
            if let Some(jid) = self.jid.take() {
                if jid.node().is_some() {
                    self.jid = Some(jid::Jid::from_parts(None, jid.domain(), jid.resource()));
                }
            }
        }
        Ok(())
    }

    #[getter]
    fn get_domain(&self) -> String {
        match &self.jid {
            None => String::new(),
            Some(jid) => jid.domain().to_string(),
        }
    }

    #[setter]
    fn set_domain(&mut self, domain: &str) -> PyResult<()> {
        let domain = jid::DomainPart::new(domain).map_err(to_exc)?;
        self.jid = Some(match self.jid.as_ref().map(jid::Jid::try_as_full) {
            Some(Ok(full)) => jid::FullJid::from_parts(
                full.node(),
                &domain,
                full.resource(),
            ).into(),
            Some(Err(bare)) => {
                jid::BareJid::from_parts(bare.node(), &domain).into()
            }
            None => jid::BareJid::from_parts(None, &domain).into(),
        });
        Ok(())
    }

    #[getter]
    fn get_resource(&self) -> String {
        match &self.jid {
            None => String::new(),
            Some(jid) => jid
                .resource()
                .map(ToString::to_string)
                .unwrap_or_else(String::new),
        }
    }

    #[setter]
    fn set_resource(&mut self, resource: Option<&str>) -> PyResult<()> {
        if let Some(resource) = resource {
            let resource = jid::ResourcePart::new(resource).map_err(to_exc)?;
            self.jid = Some(match self.jid.as_ref().map(jid::Jid::try_as_full) {
                Some(Ok(full)) => jid::FullJid::from_parts(
                    full.node(),
                    full.domain(),
                    &resource,
                ).into(),
                Some(Err(bare)) => {
                    bare.with_resource(&resource).into()
                }
                None => Err(InvalidJID::new_err(
                    "JID.resource must apply to a proper JID",
                ))?,
            });
        } else {
            if let Some(jid) = self.jid.take() {
                self.jid = Some(jid.into_bare().into());
            }
        }
        Ok(())
    }

    /// Use the full JID as the string value.
    fn __str__(&self) -> String {
        match &self.jid {
            None => String::new(),
            Some(jid) => jid.to_string(),
        }
    }

    /// Use the full JID as the representation.
    fn __repr__(&self) -> String {
        match &self.jid {
            None => String::new(),
            Some(jid) => jid.to_string(),
        }
    }

    /// Two JIDs are equal if they have the same full JID value.
    fn __richcmp__(&self, other: &Bound<'_, PyAny>, op: pyo3::basic::CompareOp) -> PyResult<bool> {
        let other = if let Ok(other) = other.extract::<PyRef<PyJid>>() {
            other
        } else if other.is_none() {
            Bound::new(other.py(), PyJid::new(None, false)?)?.borrow()
        } else {
            match PyJid::new(Some(other), false) {
                Ok(res) => Bound::new(other.py(), res)?.borrow(),
                Err(_) => return Ok(false),
            }
        };
        match (&self.jid, &other.jid) {
            (None, None) => Ok(true),
            (Some(jid), Some(other)) => match op {
                pyo3::basic::CompareOp::Eq => Ok(jid == other),
                pyo3::basic::CompareOp::Ne => Ok(jid != other),
                _ => Err(PyNotImplementedError::new_err(
                    "Only == and != are implemented",
                )),
            },
            _ => Ok(false),
        }
    }

    /// Hash a JID based on the string version of its full JID.
    fn __hash__(&self, py: Python) -> PyResult<isize> {
        if let Some(jid) = &self.jid {
            // Use the same algorithm as the Python JID.
            PyString::new(py, jid.as_str()).hash()
        } else {
            Ok(0)
        }
    }

    fn __getstate__(&self, py: Python) -> PyResult<Option<PyObject>> {
        match &self.jid {
            Some(jid) => Ok(Some(PyString::new(py, jid.as_str()).into())),
            None => Ok(None)
        }
    }

    fn __setstate__(&mut self, py: Python, state: PyObject) -> PyResult<()> {
        if state.is_none(py) {
            self.jid = None;
        } else {
            let string = state.extract(py)?;
            self.jid = Some(jid::Jid::new(string).unwrap());
        }
        Ok(())
    }

    // Aliases

    #[getter]
    fn get_user(&self) -> String {
        self.get_node()
    }

    #[setter]
    fn set_user(&mut self, user: Option<&str>) -> PyResult<()> {
        self.set_node(user)
    }

    #[getter]
    fn get_local(&self) -> String {
        self.get_node()
    }

    #[setter]
    fn set_local(&mut self, local: Option<&str>) -> PyResult<()> {
        self.set_node(local)
    }

    #[getter]
    fn get_username(&self) -> String {
        self.get_node()
    }

    #[setter]
    fn set_username(&mut self, username: Option<&str>) -> PyResult<()> {
        self.set_node(username)
    }

    #[getter]
    fn get_server(&self) -> String {
        self.get_domain()
    }

    #[setter]
    fn set_server(&mut self, server: &str) -> PyResult<()> {
        self.set_domain(server)
    }

    #[getter]
    fn get_host(&self) -> String {
        self.get_domain()
    }

    #[setter]
    fn set_host(&mut self, host: &str) -> PyResult<()> {
        self.set_domain(host)
    }

    #[getter]
    fn get_jid(&self) -> String {
        self.get_full()
    }

    #[setter]
    fn set_jid(&mut self, jid: &str) -> PyResult<()> {
        self.set_full(jid)
    }
}

#[pymodule]
#[pyo3(name = "jid")]
fn py_jid(py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyJid>()?;
    m.add("InvalidJID", py.get_type::<InvalidJID>())?;
    Ok(())
}
