const urlInput = document.getElementById('url-input')
const htmlInput = document.getElementById('html-input')
const lintForm = document.getElementById('lint-form')
const reportDiv = document.getElementById('report')

function toggleFields() {
	if (urlInput.value.trim()) {
		htmlInput.disabled = true
	} else {
		htmlInput.disabled = false
	}
	if (htmlInput.value.trim()) {
		urlInput.disabled = true
	} else {
		urlInput.disabled = false
	}
}

urlInput.addEventListener('input', toggleFields)
htmlInput.addEventListener('input', toggleFields)

lintForm.addEventListener('submit', async e => {
	e.preventDefault()
	reportDiv.innerHTML =
		'<div class="spinner-border" role="status"><span class="visually-hidden">Loading…</span></div>'

	let endpoint, payload
	const url = urlInput.value.trim()
	const html = htmlInput.value.trim()

	if (url) {
		endpoint = '/api/lint-url'
		payload = { url }
	} else if (html) {
		endpoint = '/api/lint-html'
		payload = { html }
	} else {
		reportDiv.innerHTML =
			'<div class="alert alert-warning">Enter URL or HTML.</div>'
		return
	}

	try {
		const resp = await fetch(endpoint, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload),
		})
		const data = await resp.json()
		if (!resp.ok) throw new Error(data.detail || 'Error')
		renderReport(data)
	} catch (err) {
		reportDiv.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`
	}
})

function renderReport(data) {
	if (data.issues.length === 0) {
		reportDiv.innerHTML =
			'<div class="alert alert-success">No issues found!</div>'
		return
	}

	let html = `
    <h4>Summary</h4>
    <ul>
      <li>Total: ${data.summary.total}</li>
      <li>Errors: ${data.summary.errors}</li>
      <li>Warnings: ${data.summary.warnings}</li>
    </ul>
    <h4>Issues</h4>
    <table class="table table-sm table-striped">
      <thead>
        <tr>
          <th>Code</th>
          <th>Message</th>
          <th>Selector</th>
          <th>Context</th>
        </tr>
      </thead>
      <tbody>
  `

	data.issues.forEach(issue => {
		const ctx = issue.context || ''
		const needsTooltip = ctx.length > 50
		const shortCtx = needsTooltip
			? ctx.slice(0, 50).replace(/</g, '&lt;').replace(/>/g, '&gt;') + '…'
			: ctx.replace(/</g, '&lt;').replace(/>/g, '&gt;')

		const tooltipAttr = needsTooltip
			? ` data-bs-toggle="tooltip" title="${ctx.replace(/"/g, '&quot;')}" `
			: ''

		html += `
      <tr>
        <td>${issue.code}</td>
        <td>${issue.message}</td>
        <td>${issue.selector || '-'}</td>
        <td>
          <span${tooltipAttr}>
            <code>${shortCtx || '-'}</code>
          </span>
        </td>
      </tr>
    `
	})

	html += `
      </tbody>
    </table>
  `
	reportDiv.innerHTML = html

	document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
		new bootstrap.Tooltip(el)
	})
}
