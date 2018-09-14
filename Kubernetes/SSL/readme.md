We have two methods to create all certificates that used in a useable kubernetes clutster
1. [OpenSSL](./OpenSSL) --- deprecated.
2. [CFSSL](./CFSSl)


until now, I have more understanding of the certificatess, in a kubernetes, we have at [least three CA certs](https://github.com/kubernetes-incubator/apiserver-builder/blob/master/docs/concepts/auth.md#certificates-overview)

1. a serving CA: this CA signs "serving" certificates, which are used to encrypt communication over HTTPS. The same CA used to sign the main Kubernetes API server serving certificate pair may also be used to sign the addon API server serving certificates, but a different CA may also be used.

By default, addon API servers automatically generate self-signed certificates if no serving certificates are passed in, making this CA optional. However, in a real setup, you'll need this CA so that clients can easily trust the identity of the addon API server.

2. a client CA: this CA signs client certificates, and is used by the addon API server to authenticate users based on the client certificates they submit. The same client CA may be used for both the main Kubernetes API server as well as addon API servers, but a different CA may also be used. Using the same CA ensures that identity trust works the same way between the main Kubernetes API server and the addon API servers.

As an example, the default cluster admin user generated in many Kubernetes setups uses client certificate authentication. Additionally, controllers or non-human clients running outside the cluster often use certificate-based authentication.

3. a RequestHeader client CA: this special CA signs proxy client certificates. Clients presenting these certificates are effectively trusted to masquerade as any other identity. When running behind the API aggregator, this must be the same CA used to sign the aggregator's proxy client certificate. When not running with an aggregator (e.g. pre-Kubernetes-1.7, without a separate aggregator pod), this simply needs to exist.