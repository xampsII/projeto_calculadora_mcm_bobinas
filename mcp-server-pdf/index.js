#!/usr/bin/env node

const fs = require("fs");

// Pega o caminho do PDF da linha de comando
const filePath = process.argv[2];

if (!filePath) {
  console.error("Por favor, informe o caminho do PDF.");
  process.exit(1);
}

// Função melhorada para extrair texto de PDF
function extractBasicText(buffer) {
  try {
    // Tentar diferentes estratégias de extração
    
    // Estratégia 1: Buscar por strings entre parênteses (texto de PDF)
    const text = buffer.toString('latin1', 0, Math.min(buffer.length, 50000));
    const textMatches = text.match(/\([^)]{2,50}\)/g);
    if (textMatches && textMatches.length > 5) {
      const extracted = textMatches
        .map(match => match.slice(1, -1)) // Remove parênteses
        .filter(t => t.length > 2 && !/^[\s\d\-\.]+$/.test(t)) // Filtra strings vazias
        .join(' ');
      
      if (extracted.length > 50) {
        return extracted;
      }
    }
    
    // Estratégia 2: Buscar por padrões de texto comum
    const commonPatterns = [
      /CNPJ[:\s]*(\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2})/gi,
      /(\d{2}\/\d{2}\/\d{4})/g,
      /R\$\s*([\d.,]+)/gi,
      /Nota.*?(\d+)/gi,
      /Total.*?([\d.,]+)/gi
    ];
    
    let extractedText = '';
    commonPatterns.forEach(pattern => {
      const matches = text.match(pattern);
      if (matches) {
        extractedText += matches.join(' ') + ' ';
      }
    });
    
    if (extractedText.length > 20) {
      return extractedText.trim();
    }
    
    return "Não foi possível extrair texto legível deste PDF. O arquivo pode estar corrompido ou usar formato não suportado.";
  } catch (error) {
    return `Erro ao processar PDF: ${error.message}`;
  }
}

const dataBuffer = fs.readFileSync(filePath);

try {
  const extractedText = extractBasicText(dataBuffer);
  
  console.log(JSON.stringify({
    text: extractedText,
    filename: filePath.split('/').pop() || filePath.split('\\').pop()
  }, null, 2));
} catch (error) {
  console.log(JSON.stringify({
    text: `Erro ao processar PDF: ${error.message}`,
    filename: filePath.split('/').pop() || filePath.split('\\').pop()
  }, null, 2));
}
