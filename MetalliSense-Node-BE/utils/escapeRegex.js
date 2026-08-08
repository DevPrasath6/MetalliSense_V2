// Escapes regex metacharacters so untrusted input can be safely used inside `new RegExp(...)`
module.exports = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
