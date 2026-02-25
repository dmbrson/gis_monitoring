export const escapeHtml = (str) => {
  if (typeof str !== 'string') return ''
  const div = document.createElement('div')
  div.textContent = str
  return div.innerHTML
}

export const sanitizeObject = (obj, fields = []) => {
  const result = { ...obj }
  fields.forEach(field => {
    if (result[field] != null) {
      result[field] = escapeHtml(result[field])
    }
  })
  return result
}