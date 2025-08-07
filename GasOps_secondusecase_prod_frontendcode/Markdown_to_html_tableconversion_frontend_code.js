// =============================================================================
// MARKDOWN TABLE TO HTML CONVERSION FUNCTIONS
// =============================================================================

/**
 * Parses markdown text and extracts tables, returning segments of text and tables
 * @param {string} text - The markdown text containing tables
 * @returns {Array|null} - Array of segments with type 'text' or 'table', or null if no tables found
 */
const parseAllMarkdownTables = (text) => {
  // Validate input
  if (typeof text !== 'string' || !text) {
    return null;
  }

  const lines = text.split('\n');
  const tables = [];
  let currentTableStart = -1;
  let currentTableEnd = -1;
  let inTable = false;
  
  // Scan through each line to find table boundaries
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // Check if line contains table markers (pipes)
    if (line.includes('|') && line.split('|').length > 2) {
      if (!inTable) {
        inTable = true;
        currentTableStart = i;
      }
      currentTableEnd = i;
    } else if (inTable && (line === '' || !line.includes('|'))) {
      // End of current table detected
      if (currentTableStart !== -1 && currentTableEnd !== -1) {
        const tableText = lines.slice(currentTableStart, currentTableEnd + 1);
        
        // Clean and parse table rows
        const rows = tableText
          .filter(line => {
            const trimmed = line.trim();
            return trimmed && 
                   !trimmed.match(/^\s*\|[\s\-:]+\|\s*$/) && // Remove separator rows
                   !trimmed.match(/^\s*\|[\s\-]+\|\s*[\s\-]+\|\s*$/) && // Remove dashed separators
                   !trimmed.match(/^[\s\-\|]+$/) && // Remove lines with only dashes, spaces, and pipes
                   trimmed.includes('|') && 
                   trimmed.split('|').filter(cell => cell.trim()).length >= 2;
          })
          .map(line => 
            line.split('|')
              .map(cell => cell.trim())
              .filter((cell, index, arr) => index !== 0 && index !== arr.length - 1) // Remove empty edge cells
          );

        // Only add if we have at least header + 1 data row
        if (rows.length >= 2) {
          tables.push({
            startLine: currentTableStart,
            endLine: currentTableEnd,
            tableData: rows
          });
        }
      }
      inTable = false;
      currentTableStart = -1;
      currentTableEnd = -1;
    }
  }
  
  // Handle table at end of text
  if (inTable && currentTableStart !== -1) {
    const tableText = lines.slice(currentTableStart, currentTableEnd + 1);
    const rows = tableText
      .filter(line => {
        const trimmed = line.trim();
        return trimmed && 
               !trimmed.match(/^\s*\|[\s\-:]+\|\s*$/) && 
               !trimmed.match(/^\s*\|[\s\-]+\|\s*[\s\-]+\|\s*$/) && 
               !trimmed.match(/^[\s\-\|]+$/) && 
               trimmed.includes('|') && 
               trimmed.split('|').filter(cell => cell.trim()).length >= 2;
      })
      .map(line => 
        line.split('|')
          .map(cell => cell.trim())
          .filter((cell, index, arr) => index !== 0 && index !== arr.length - 1)
      );

    if (rows.length >= 2) {
      tables.push({
        startLine: currentTableStart,
        endLine: currentTableEnd,
        tableData: rows
      });
    }
  }

  if (tables.length === 0) return null;

  // Build segments alternating between text and tables
  const segments = [];
  let lastEnd = -1;

  tables.forEach((table, index) => {
    // Add text content before this table
    const textBefore = lines.slice(lastEnd + 1, table.startLine).join('\n').trim();
    if (textBefore) {
      segments.push({ type: 'text', content: textBefore });
    }
    
    // Add the table
    segments.push({ type: 'table', content: table.tableData });
    lastEnd = table.endLine;
  });

  // Add any remaining text after the last table
  const textAfter = lines.slice(lastEnd + 1).join('\n').trim();
  if (textAfter) {
    segments.push({ type: 'text', content: textAfter });
  }

  return segments;
};

/**
 * Renders a parsed markdown table as HTML table element
 * @param {Array} rows - Array of arrays, first row is headers, rest are data
 * @returns {JSX.Element|null} - HTML table component or null if invalid data
 */
const renderMarkdownTable = (rows) => {
  if (!rows || rows.length < 1) return null;
  
  const headers = rows[0];
  const dataRows = rows.slice(1);
  
  return (
    <div className="chat-table-container" style={{
      overflowX: 'auto', 
      margin: '8px 0', 
      display: 'flex', 
      justifyContent: 'flex-start'
    }}>
      <table className="chat-table" style={{
        borderCollapse: 'collapse', 
        width: 'auto', 
        maxWidth: '600px',
        minWidth: '300px',
        border: '1px solid #ccc',
        fontSize: '14px',
        fontFamily: 'Font Awesome 6 Free'
      }}>
        <thead>
          <tr>
            {headers.map((header, idx) => (
              <th key={idx} style={{
                border: '1px solid #ccc', 
                padding: '6px 8px', 
                background: '#f5f5f5',
                fontWeight: '600',
                textAlign: 'left',
                fontSize: '14px',
                color: '#333',
                whiteSpace: 'nowrap',
                minWidth: '80px',
                fontFamily: 'Font Awesome 6 Free'
              }}>
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {dataRows.map((row, rowIdx) => (
            <tr key={rowIdx} style={{background: '#fff'}}>
              {row.map((cell, cellIdx) => (
                <td key={cellIdx} style={{
                  border: '1px solid #ccc', 
                  padding: '6px 8px',
                  textAlign: 'left',
                  fontSize: '14px',
                  color: '#333',
                  lineHeight: '1.3',
                  whiteSpace: 'nowrap',
                  fontFamily: 'Font Awesome 6 Free'
                }}>
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

/**
 * Converts basic markdown formatting to HTML for text content
 * @param {string} text - Text with markdown formatting
 * @returns {string} - HTML formatted text
 */
const renderMarkdownText = (text) => {
  if (!text) return '';
  
  // Process each line for markdown formatting
  const lines = text.split('\n').map(line => {
    // Convert headers
    if (line.trim().startsWith('### ')) {
      return `<h3 style="font-size: 1.1em; font-weight: 600; margin: 8px 0 6px 0; color: #2c3e50;">${line.replace('### ', '')}</h3>`;
    }
    if (line.trim().startsWith('## ')) {
      return `<h2 style="font-size: 1.2em; font-weight: 600; margin: 10px 0 6px 0; color: #2c3e50;">${line.replace('## ', '')}</h2>`;
    }
    if (line.trim().startsWith('# ')) {
      return `<h1 style="font-size: 1.3em; font-weight: 600; margin: 12px 0 8px 0; color: #2c3e50;">${line.replace('# ', '')}</h1>`;
    }
    
    // Convert bold and italic text
    line = line.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #2c3e50; font-weight: 600;">$1</strong>');
    line = line.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Convert horizontal rules
    if (line.trim() === '---') {
      return '<hr style="border: none; border-top: 1px solid #ddd; margin: 8px 0;" />';
    }
    
    return line;
  });
  
  return lines.join('\n');
};

// =============================================================================
// USAGE EXAMPLE IN YOUR COMPONENT
// =============================================================================

// Inside your message rendering logic:

// Check if the message text contains markdown tables
const markdownSegments = parseAllMarkdownTables(textContent);
if (markdownSegments) {
  return (
    <div style={{maxWidth: '650px', width: 'fit-content'}}>
      {markdownSegments.map((segment, index) => {
        if (segment.type === 'text') {
          // Render text with basic markdown formatting
          return (
            <div 
              key={index} 
              style={{
                marginBottom: '6px',
                lineHeight: '1.4',
                fontSize: '14px',
                maxWidth: '600px',
                width: 'fit-content',
                fontFamily: 'Font Awesome 6 Free',
                fontWeight: '500',
                textAlign: 'left'
              }}
              dangerouslySetInnerHTML={{
                __html: renderMarkdownText(segment.content)
              }}
            />
          );
        } else if (segment.type === 'table') {
          // Render table as HTML table
          return (
            <div key={index} style={{margin: '4px 0'}}>
              {renderMarkdownTable(segment.content)}
            </div>
          );
        }
        return null;
      })}
    </div>
  );
}