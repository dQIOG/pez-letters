<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:_="urn:local"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math"
    exclude-result-prefixes="#all"
    version="3.0">
    <xsl:output method="xml" indent="no"/>
    <xsl:function name="_:moduleByEltName">
        <xsl:param name="eltName"/>
        <xsl:variable name="eltSpec" select="doc($path-to-tei-specs||'/'||$eltName||'.xml')"/>
        <xsl:value-of select="$eltSpec//@module"/>
    </xsl:function>
    <xsl:param name="path-to-tei-specs">/home/danielschopper/data/TEI/P5/Source/Specs</xsl:param>
    <xsl:param name="path-to-docs">file:/home/danielschopper/data/pez-letters/data/editions/</xsl:param>
    <xsl:template match="/">
        <xsl:variable name="eltNames" select="distinct-values(collection($path-to-docs)//*/local-name(.))"/>
        <_>
            <xsl:for-each-group select="$eltNames" group-by="_:moduleByEltName(.)">
                <xsl:sort select="current-grouping-key()"/>
                <moduleRef key="{current-grouping-key()}" select="{string-join(sort(current-group()),' ')}"/>
            </xsl:for-each-group>
        </_>
    </xsl:template>
</xsl:stylesheet>