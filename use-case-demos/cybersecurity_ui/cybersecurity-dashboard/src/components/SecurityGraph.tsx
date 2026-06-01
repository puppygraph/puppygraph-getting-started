'use client';
import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';
import { Box, Typography, Card, CardContent, Chip, useTheme, Theme, Popover, IconButton } from '@mui/material';
import { 
  Memory as InstanceIcon,
  Shield as SecurityIcon,
  Hub as NetworkIcon,
  CloudQueue as CloudIcon,
  Public as ExternalIcon,
  Dangerous as CVEIcon,
  ReportProblem as FindingIcon,
  MoreHoriz as MoreIcon,
  Info as InfoIcon
} from '@mui/icons-material';

interface SecurityGraphNode {
  id: string;
  type: 'cve' | 'instance' | 'public_instance' | 'lateral_target' | 'network' | 'subnet' | 'external' | 'vulnerability' | 'more' | 'external_combined';
  label: string;
  severity?: 'critical' | 'high' | 'medium' | 'low';
  details?: string;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
  isMore?: boolean;
  moreType?: string;
  externalIps?: string[];
  isExpanded?: boolean;
}

interface SecurityGraphLink extends d3.SimulationLinkDatum<SecurityGraphNode> {
  source: string | SecurityGraphNode;
  target: string | SecurityGraphNode;
  type: 'exploits' | 'communicates' | 'accesses' | 'lateral_movement';
  label: string;
}

type SecurityViewType = 
  | 'cve_impact'
  | 'lateral_movement'
  | 'public_network_access'
  | 'network_security'
  | 'infrastructure_map'
  | 'default';

interface SecurityGraphData {
  nodes: SecurityGraphNode[];
  links: SecurityGraphLink[];
  query?: string;
  viewType?: SecurityViewType;
}

interface SecurityGraphProps {
  data: SecurityGraphData;
  width?: number;
  height?: number;
  resetKey?: string | number;
  showInfoPanel?: boolean;
}

const getNodeIcon = (type: string) => {
  switch (type) {
    case 'cve':
      return CVEIcon;
    case 'vulnerability':
      return FindingIcon;
    case 'instance':
    case 'public_instance':
    case 'lateral_target':
      return InstanceIcon;
    case 'network':
      return NetworkIcon;
    case 'subnet':
      return CloudIcon;
    case 'external':
      return ExternalIcon;
    case 'external_combined':
      return ExternalIcon;
    case 'more':
      return MoreIcon;
    default:
      return SecurityIcon;
  }
};

const getNodeColor = (theme: Theme, type: string) => {
  switch (type) {
    case 'cve':
      return '#e53e3e'; // Red for CVEs
    case 'vulnerability':
      return '#dd6b20'; // Orange for vulnerability findings
    case 'instance':
      return '#3182ce'; // Blue for EC2 instances
    case 'public_instance':
      return '#e53e3e'; // Red for public affected instances
    case 'lateral_target':
      return '#805ad5'; // Purple for lateral movement targets
    case 'network':
      return '#38a169'; // Green for network interfaces
    case 'subnet':
      return '#805ad5'; // Purple for subnets
    case 'external':
      return '#d69e2e'; // Yellow/Gold for external IPs
    case 'external_combined':
      return '#d69e2e'; // Yellow/Gold for combined external IPs
    case 'more':
      return theme.palette.grey[400]; // Grey for more nodes
    default:
      return theme.palette.grey[500];
  }
};

const getLinkColor = (theme: Theme, type: string) => {
  switch (type) {
    case 'exploits':
      return theme.palette.error.main;
    case 'communicates':
      return theme.palette.info.main;
    case 'accesses':
      return theme.palette.warning.main;
    case 'lateral_movement':
      return theme.palette.secondary.main;
    default:
      return theme.palette.grey[400];
  }
};

export default function SecurityGraph({ data, width, height = 500, resetKey, showInfoPanel = true }: SecurityGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<SecurityGraphNode | null>(null);
  const [, setHoveredNode] = useState<SecurityGraphNode | null>(null);
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height });
  const [expandedExternalNodes, setExpandedExternalNodes] = useState<Set<string>>(new Set());
  const [processedGraphData, setProcessedGraphData] = useState<SecurityGraphData | null>(null);
  const [savedTransform, setSavedTransform] = useState<d3.ZoomTransform | null>(null);
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(showInfoPanel);
  const theme = useTheme();

  // Get view content based on explicit view type
  const getViewContent = useCallback(() => {
    const viewType = processedGraphData?.viewType || data.viewType || 'default';
    
    switch (viewType) {
      case 'cve_impact':
        return {
          title: 'CVE Impact Analysis',
          description: 'Visualizing vulnerability exploitation paths and affected infrastructure components.',
          analysis: [
            'Trace CVE propagation through security findings',
            'Identify vulnerable instances and network exposure',
            'Assess potential blast radius of exploitation',
            'Prioritize remediation based on connectivity'
          ]
        };
        
      case 'lateral_movement':
        return {
          title: 'Lateral Movement Risk',
          description: 'Analyzing network connectivity to understand the attack risk if public accessible nodes are compromised.',
          analysis: [
            'Map potential lateral movement from compromised public nodes',
            'Identify internal systems reachable after initial breach',
            'Assess network segmentation effectiveness against attacks',
            'Evaluate blast radius of public node compromise'
          ]
        };
        
      case 'public_network_access':
        return {
          title: 'Public Network Access',
          description: 'Identifying instances with public network exposures that could be higher risk to certain attacks such as log4shell which requires accessing a LDAP server.',
          analysis: [
            'Detect instances with direct internet connectivity',
            'Assess log4shell attack vectors via LDAP server access',
            'Identify remote code execution opportunities',
            'Monitor public-facing services for exploitation risks'
          ]
        };
        
      case 'network_security':
        return {
          title: 'Network Security Analysis',
          description: 'Mapping network traffic patterns and external connectivity risks.',
          analysis: [
            'Monitor traffic to external IP addresses',
            'Detect suspicious communication patterns',
            'Analyze network segmentation effectiveness',
            'Identify potential data exfiltration paths'
          ]
        };
        
      case 'infrastructure_map':
        return {
          title: 'Infrastructure Security Map',
          description: 'Overview of AWS infrastructure components and their security relationships.',
          analysis: [
            'Visualize infrastructure connectivity',
            'Understand security group relationships',
            'Monitor cross-subnet communications',
            'Identify security control gaps'
          ]
        };
        
      default:
        return {
          title: 'Security Graph Analysis',
          description: 'Interactive visualization of cybersecurity relationships across your AWS infrastructure.',
          analysis: [
            'Explore security entity relationships',
            'Analyze attack surface exposure',
            'Understand infrastructure dependencies',
            'Investigate security incidents'
          ]
        };
    }
  }, [data.viewType, processedGraphData?.viewType]);

  // Process data to combine ALL external IPs into single node
  const processGraphData = useCallback((originalData: SecurityGraphData): SecurityGraphData => {
    const nodes: SecurityGraphNode[] = [];
    const links: SecurityGraphLink[] = [];
    const nodeIds = new Set<string>();
    const networkToExternalLinks: SecurityGraphLink[] = [];
    
    // Find all external nodes and network->external links
    const externalNodes: SecurityGraphNode[] = [];
    originalData.nodes.forEach(node => {
      if (node.type === 'external') {
        externalNodes.push(node);
      } else {
        nodes.push(node);
        nodeIds.add(node.id);
      }
    });
    
    // Collect all links to external nodes (from any source type)
    originalData.links.forEach(link => {
      const targetNode = originalData.nodes.find(n => n.id === (typeof link.target === 'string' ? link.target : link.target.id));
      
      if (targetNode?.type === 'external') {
        // Any link pointing to an external node
        networkToExternalLinks.push(link);
      } else {
        // Keep other links as they are
        const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
        const targetId = typeof link.target === 'string' ? link.target : link.target.id;
        if (nodeIds.has(sourceId) && nodeIds.has(targetId)) {
          links.push(link);
        }
      }
    });
    
    // Create single combined external node or individual nodes based on expansion state
    const combinedId = 'external-combined-all';
    const isExpanded = expandedExternalNodes.has(combinedId);
    
    if (externalNodes.length > 0) {
      if (isExpanded) {
        // Add individual external nodes when expanded
        externalNodes.forEach(node => {
          nodes.push(node);
          nodeIds.add(node.id);
        });
        
        // Add original network->external links when expanded
        networkToExternalLinks.forEach(link => {
          const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
          const targetId = typeof link.target === 'string' ? link.target : link.target.id;
          if (nodeIds.has(sourceId) && nodeIds.has(targetId)) {
            links.push(link);
          }
        });
      } else {
        // Add single combined node when collapsed
        const maliciousCount = externalNodes.filter(n => n.severity === 'critical').length;
        const totalCount = externalNodes.length;
        
        nodes.push({
          id: combinedId,
          type: 'external_combined',
          label: `${totalCount} External IPs`,
          severity: maliciousCount > 0 ? 'critical' : 'low',
          details: `${totalCount} external IP addresses\n${maliciousCount} potentially malicious\nClick to expand`,
          externalIps: externalNodes.map(n => n.label),
          isExpanded: false
        });
        nodeIds.add(combinedId);
        
        // Create links from any source to the combined node
        const sourceIds = new Set<string>();
        networkToExternalLinks.forEach(link => {
          const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
          sourceIds.add(sourceId);
        });
        
        // Add one link per source to the combined external node
        sourceIds.forEach(sourceId => {
          if (nodeIds.has(sourceId)) {
            links.push({
              source: sourceId,
              target: combinedId,
              type: 'communicates',
              label: 'External Access'
            });
          }
        });
      }
    } else {
      // No external nodes, just add other links
      originalData.links.forEach(link => {
        const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
        const targetId = typeof link.target === 'string' ? link.target : link.target.id;
        if (nodeIds.has(sourceId) && nodeIds.has(targetId)) {
          links.push(link);
        }
      });
    }
    
    return { nodes, links, query: originalData.query, viewType: originalData.viewType };
  }, [expandedExternalNodes]);

  // Effect to handle dynamic resizing
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const containerWidth = containerRef.current.offsetWidth;
        setDimensions({
          width: width || Math.max(800, containerWidth - 32), // Subtract padding
          height
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    
    return () => window.removeEventListener('resize', updateDimensions);
  }, [width, height]);

  // Reset expanded external nodes when resetKey changes (view switching)
  useEffect(() => {
    if (resetKey !== undefined) {
      setExpandedExternalNodes(new Set());
    }
  }, [resetKey]);

  // Process graph data when input data or expanded state changes
  useEffect(() => {
    if (data && data.nodes.length > 0) {
      setProcessedGraphData(processGraphData(data));
    }
  }, [data, expandedExternalNodes, processGraphData]);

  useEffect(() => {
    if (!svgRef.current || !processedGraphData || !processedGraphData.nodes.length) return;
    
    const { height: svgHeight } = dimensions;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const container = svg.append('g');
    
    // Calculate hierarchical layout positions
    const layers: { [key: string]: SecurityGraphNode[] } = {
      'cve': [],
      'vulnerability': [],
      'instance': [],
      'public_instance': [],
      'lateral_target': [],
      'network': [],
      'external': []
    };

    // Group nodes by type/layer
    processedGraphData.nodes.forEach(node => {
      if (layers[node.type]) {
        layers[node.type].push(node);
      } else if (node.type === 'more') {
        // Handle 'more' nodes by placing them in the appropriate layer based on moreType
        if (node.moreType && layers[node.moreType]) {
          layers[node.moreType].push(node);
        }
      } else if (node.type === 'external_combined') {
        // Place combined external nodes in external layer
        layers['external'].push(node);
      }
    });

    // Calculate positions for hierarchical layout with left-to-right, top-to-bottom ordering
    const layerOrder = ['cve', 'vulnerability', 'instance', 'public_instance', 'lateral_target', 'network', 'external'];
    
    // Filter out empty layers to handle odd/even indexing correctly
    const nonEmptyLayers = layerOrder.filter(layerType => layers[layerType].length > 0);
    
    const layerGap = 180; // Fixed gap between layers
    const padding = 60;
    const verticalSpacing = 90; // Vertical spacing between nodes in same column
    
    // Calculate how many rows we can fit based on available height
    const availableHeight = svgHeight - 2 * padding;
    const maxRowsPerLayer = Math.max(1, Math.floor(availableHeight / verticalSpacing));
    
    let currentX = layerGap / 2; // Start with half gap from left

    nonEmptyLayers.forEach((layerType) => {
      const nodesInLayer = layers[layerType];

      // Determine rows needed based on available height
      const rows = Math.min(maxRowsPerLayer, Math.ceil(nodesInLayer.length / Math.ceil(nodesInLayer.length / maxRowsPerLayer)));
      const nodesPerRow = Math.ceil(nodesInLayer.length / rows);
      
      // Calculate layer dimensions and centering
      const layerTotalHeight = (rows - 1) * verticalSpacing;
      const startY = (svgHeight - layerTotalHeight) / 2;
      
      nodesInLayer.forEach((node, nodeIndex) => {
        // Left-to-right, then top-to-bottom ordering within layer
        const rowIndex = Math.floor(nodeIndex / nodesPerRow);
        const columnIndex = nodeIndex % nodesPerRow;
        
        // Calculate actual nodes in this specific row
        const actualNodesInRow = Math.min(nodesPerRow, nodesInLayer.length - rowIndex * nodesPerRow);
        
        // X position: distribute nodes horizontally within the layer
        const horizontalSpacing = 120; // Horizontal spacing between nodes in same row
        
        if (actualNodesInRow === 1) {
          // Single node - center it in the layer
          node.x = currentX;
        } else {
          // Multiple nodes - distribute them evenly
          const startXForRow = currentX;
          node.x = startXForRow + columnIndex * horizontalSpacing;
        }
        
        // Y position: honeycomb layout - offset odd columns by half vertical spacing
        const isOddColumn = columnIndex % 2 === 1;
        const honeycombOffset = isOddColumn ? verticalSpacing / 2 : 0;
        node.y = startY + rowIndex * verticalSpacing + honeycombOffset;
      });
      
      // Move to next layer position based on rightmost node of current layer
      const rightmostNodeX = Math.max(...nodesInLayer.map(node => node.x || 0));
      const nodeRadius = 28; // Maximum node radius
      currentX = rightmostNodeX + nodeRadius + layerGap;
    });

    // Create zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Add click handler to close popover when clicking on empty space
    svg.on('click', (event) => {
      if (event.target === event.currentTarget) {
        setAnchorEl(null);
        setSelectedNode(null);
      }
    });

    // Arrow markers removed for cleaner appearance

    // Create links with straight left-to-right paths
    container.append('g')
      .selectAll('path')
      .data(processedGraphData.links)
      .enter().append('path')
      .attr('class', 'graph-link')
      .attr('fill', 'none')
      .attr('stroke', d => getLinkColor(theme, d.type))
      .attr('stroke-width', 2)
      // No arrow markers
      .attr('opacity', 0.7)
      .attr('d', d => {
        const source = processedGraphData.nodes.find(n => n.id === (typeof d.source === 'string' ? d.source : d.source.id));
        const target = processedGraphData.nodes.find(n => n.id === (typeof d.target === 'string' ? d.target : d.target.id));
        
        if (!source || !target) {
          console.warn('Missing source or target node for link:', d);
          return '';
        }
        
        // Calculate connection points: right side of source node to left side of target node
        const sourceRadius = source.type === 'cve' ? 28 : 22;
        const targetRadius = target.type === 'cve' ? 28 : 22;
        
        const sourceX = source.x! + sourceRadius;
        const sourceY = source.y!;
        const targetX = target.x! - targetRadius;
        const targetY = target.y!;
        
        // Create curved line with double curve style
        const controlOffset = Math.abs(targetY - sourceY) * 0.3 + 30; // Control point offset
        
        return `M${sourceX},${sourceY}C${sourceX + controlOffset},${sourceY} ${targetX - controlOffset},${targetY} ${targetX},${targetY}`;
      });

    // Link labels removed for cleaner appearance

    // Helper function to get connected nodes and links (both incoming and outgoing)
    const getConnectedElements = (nodeId: string) => {
      const connectedNodes = new Set<string>();
      const connectedLinks = new Set<number>();
      
      processedGraphData.links.forEach((link, index) => {
        const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
        const targetId = typeof link.target === 'string' ? link.target : link.target.id;
        
        // Check for outgoing edges (node is source)
        if (sourceId === nodeId) {
          connectedNodes.add(targetId);
          connectedLinks.add(index);
        }
        // Check for incoming edges (node is target)
        if (targetId === nodeId) {
          connectedNodes.add(sourceId);
          connectedLinks.add(index);
        }
      });
      
      return { connectedNodes, connectedLinks };
    };

    // Create node groups
    const node = container.append('g')
      .selectAll('g')
      .data(processedGraphData.nodes)
      .enter().append('g')
      .attr('class', 'graph-node')
      .attr('cursor', 'pointer')
      .attr('transform', d => `translate(${d.x}, ${d.y})`)
      .on('click', (event, d) => {
        event.stopPropagation();
        
        if (d.type === 'external_combined') {
          // Save current zoom/pan transform before expanding
          const currentTransform = d3.zoomTransform(svg.node()!);
          setSavedTransform(currentTransform);
          
          // Toggle expansion for combined external IP node
          const newExpanded = new Set(expandedExternalNodes);
          if (expandedExternalNodes.has(d.id)) {
            newExpanded.delete(d.id);
          } else {
            newExpanded.add(d.id);
          }
          setExpandedExternalNodes(newExpanded);
        } else {
          setSelectedNode(d);
          // Use the actual clicked element as anchor
          setAnchorEl(event.currentTarget as HTMLElement);
        }
      })
      .on('mouseenter', (event, d) => {
        setHoveredNode(d);
        
        // Get connected elements
        const { connectedNodes, connectedLinks } = getConnectedElements(d.id);
        
        // Dim all links and nodes first
        container.selectAll('.graph-link')
          .attr('opacity', 0.2)
          .attr('stroke-width', 1);
        
        container.selectAll('.graph-node')
          .attr('opacity', 0.4);
        
        // Highlight connected links
        container.selectAll('.graph-link')
          .filter((_linkData, index: number) => connectedLinks.has(index))
          .attr('opacity', 1)
          .attr('stroke-width', 3);
        
        // Highlight current node and connected nodes
        container.selectAll('.graph-node')
          .filter((nodeData) => (nodeData as SecurityGraphNode).id === d.id || connectedNodes.has((nodeData as SecurityGraphNode).id))
          .attr('opacity', 1);
      })
      .on('mouseleave', () => {
        setHoveredNode(null);
        
        // Reset all elements to normal state
        container.selectAll('.graph-link')
          .attr('opacity', 0.7)
          .attr('stroke-width', 2);
        
        container.selectAll('.graph-node')
          .attr('opacity', 1);
      });

    // Add circles for nodes
    node.append('circle')
      .attr('class', 'node-circle')
      .attr('r', d => d.type === 'cve' ? 28 : 22)
      .attr('fill', d => getNodeColor(theme, d.type))
      .attr('stroke', theme.palette.background.paper)
      .attr('stroke-width', 3)
      .style('filter', 'drop-shadow(2px 2px 4px rgba(0,0,0,0.2))')
      .on('mouseenter', function(event, d) {
        // Scale up the circle on hover
        d3.select(this).transition().duration(200).attr('r', d.type === 'cve' ? 32 : 26);
        // Add glow effect
        d3.select(this).style('filter', 'drop-shadow(2px 2px 8px rgba(0,0,0,0.4))');
      })
      .on('mouseleave', function(event, d) {
        // Reset circle size and filter
        d3.select(this).transition().duration(200).attr('r', d.type === 'cve' ? 28 : 22);
        d3.select(this).style('filter', 'drop-shadow(2px 2px 4px rgba(0,0,0,0.2))');
      });

    // Add node labels
    node.append('text')
      .attr('dx', 0)
      .attr('dy', d => d.type === 'cve' ? 45 : 40)
      .attr('text-anchor', 'middle')
      .attr('font-size', '11px')
      .attr('font-weight', '600')
      .attr('fill', theme.palette.text.primary)
      .style('text-shadow', '1px 1px 2px rgba(255,255,255,0.8)')
      .text(d => d.label);

    // Add icons to nodes using proper Material-UI icon SVG paths
    node.append('foreignObject')
      .attr('x', -12)
      .attr('y', -12)
      .attr('width', 24)
      .attr('height', 24)
      .append('xhtml:div')
      .style('display', 'flex')
      .style('justify-content', 'center')
      .style('align-items', 'center')
      .style('width', '100%')
      .style('height', '100%')
      .style('color', theme.palette.background.paper)
      .each(function(d) {
        // Use specific SVG paths for each fancy icon type
        let iconPath = '';
        switch (d.type) {
          case 'cve':
            // Dangerous icon - warning triangle with exclamation
            iconPath = 'M15.73 3H8.27L3 8.27v7.46L8.27 21h7.46L21 15.73V8.27L15.73 3zM12 17.3c-.72 0-1.3-.58-1.3-1.3s.58-1.3 1.3-1.3 1.3.58 1.3 1.3-.58 1.3-1.3 1.3zm1-4.3h-2V7h2v6z';
            break;
          case 'vulnerability':
            // ReportProblem icon - warning triangle
            iconPath = 'M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z';
            break;
          case 'instance':
            // Memory icon - computer chip/memory
            iconPath = 'M15 9H9v6h6V9zm-2 4h-2v-2h2v2zm8-2V9h-2V7c0-1.1-.9-2-2-2h-2V3h-2v2h-2V3H9v2H7c-1.1 0-2 .9-2 2v2H3v2h2v2H3v2h2v2c0 1.1.9 2 2 2h2v2h2v-2h2v2h2v-2h2c1.1 0 2-.9 2-2v-2h2v-2h-2v-2h2zm-4 6H7V7h10v10z';
            break;
          case 'network':
            // Hub icon - network hub/switch
            iconPath = 'M12 2C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1s1-.45 1-1v-2.26c.64.16 1.31.26 2 .26s1.36-.1 2-.26V17c0 .55.45 1 1 1s1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7zm0 2c2.76 0 5 2.24 5 5s-2.24 5-5 5-5-2.24-5-5 2.24-5 5-5z';
            break;
          case 'external':
            // Public icon - globe/world
            iconPath = 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z';
            break;
          case 'external_combined':
            // Combined external - multiple globe icons or collection icon
            iconPath = 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z';
            break;
          case 'more':
            // MoreHoriz icon - three horizontal dots
            iconPath = 'M6 10c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm12 0c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm-6 0c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z';
            break;
          default:
            // Shield icon - security shield
            iconPath = 'M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11H16V16H8V11H9.2V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.4,8.7 10.4,10V11H13.6V10C13.6,8.7 12.8,8.2 12,8.2Z';
        }
        
        d3.select(this).html(`
          <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
            <path d="${iconPath}"/>
          </svg>
        `);
      });

    // Restore saved zoom/pan transform if available
    if (savedTransform) {
      svg.call(zoom.transform, savedTransform);
      setSavedTransform(null); // Clear the saved transform
    }

    // Cleanup function
    return () => {
      // No simulation to stop in hierarchical layout
    };
  }, [processedGraphData, dimensions, theme, expandedExternalNodes, savedTransform]);

  const handleClosePopover = () => {
    setAnchorEl(null);
    setSelectedNode(null);
  };

  const open = Boolean(anchorEl);

  return (
    <Box ref={containerRef} sx={{ width: '100%', height: '100%', position: 'relative' }}>
      <svg
        ref={svgRef}
        width={dimensions.width}
        height={dimensions.height}
        style={{
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: '8px',
          backgroundColor: theme.palette.background.paper,
          width: '100%'
        }}
      />
      
      {/* Unified Info Panel - Collapsible */}
      <Box
        sx={{
          position: 'absolute',
          top: 8,
          right: 8,
          zIndex: 10
        }}
      >
        {isDescriptionExpanded ? (
          <Card
            sx={{
              maxWidth: 400,
              backgroundColor: theme.palette.mode === 'dark' 
                ? 'rgba(0, 0, 0, 0.85)' 
                : 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(8px)',
              border: `1px solid ${theme.palette.divider}`,
              boxShadow: theme.shadows[4]
            }}
          >
            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem' }}>
                  {getViewContent().title}
                </Typography>
                <IconButton
                  size="small"
                  onClick={() => setIsDescriptionExpanded(false)}
                  sx={{ 
                    ml: 1,
                    color: theme.palette.text.secondary,
                    '&:hover': { backgroundColor: theme.palette.action.hover }
                  }}
                >
                  <InfoIcon fontSize="small" />
                </IconButton>
              </Box>
              
              <Typography variant="body2" sx={{ mb: 2, lineHeight: 1.5 }}>
                {getViewContent().description}
              </Typography>
              
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, fontSize: '0.875rem' }}>
                Analysis Capabilities:
              </Typography>
              <Typography variant="body2" sx={{ fontSize: '0.8rem', lineHeight: 1.4, mb: 2 }}>
                {getViewContent().analysis.map((item, index) => (
                  <span key={index}>
                    • <strong>{item.split(':')[0]}:</strong> {item.split(':').slice(1).join(':') || item}
                    {index < getViewContent().analysis.length - 1 && <br/>}
                  </span>
                ))}
              </Typography>
              
              {data.query && (
                <>
                  <Box sx={{ borderTop: `1px solid ${theme.palette.divider}`, pt: 2, mb: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, fontSize: '0.875rem' }}>
                      Current Cypher Query:
                    </Typography>
                    <Box
                      sx={{
                        backgroundColor: theme.palette.mode === 'dark' 
                          ? 'rgba(255, 255, 255, 0.05)' 
                          : 'rgba(0, 0, 0, 0.03)',
                        borderRadius: 1,
                        p: 1.5,
                        border: `1px solid ${theme.palette.divider}`,
                        maxHeight: 200,
                        overflow: 'auto'
                      }}
                    >
                      <Typography 
                        variant="body2" 
                        component="pre" 
                        sx={{ 
                          fontFamily: 'monospace',
                          fontSize: '0.75rem',
                          lineHeight: 1.4,
                          whiteSpace: 'pre-wrap',
                          margin: 0,
                          color: theme.palette.text.primary
                        }}
                      >
                        {data.query}
                      </Typography>
                    </Box>
                  </Box>
                </>
              )}
              
              <Box sx={{ borderTop: `1px solid ${theme.palette.divider}`, pt: 1.5 }}>
                <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.75rem' }}>
                  Hover over nodes to highlight connections. Click nodes for detailed information.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        ) : (
          <IconButton
            size="small"
            onClick={() => setIsDescriptionExpanded(true)}
            sx={{
              backgroundColor: theme.palette.mode === 'dark' 
                ? 'rgba(0, 0, 0, 0.8)' 
                : 'rgba(255, 255, 255, 0.9)',
              color: theme.palette.text.secondary,
              border: `1px solid ${theme.palette.divider}`,
              backdropFilter: 'blur(4px)',
              boxShadow: theme.shadows[2],
              '&:hover': {
                backgroundColor: theme.palette.primary.main,
                color: theme.palette.primary.contrastText,
                borderColor: theme.palette.primary.main
              }
            }}
          >
            <InfoIcon fontSize="small" />
          </IconButton>
        )}
      </Box>
      
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClosePopover}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'center',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'center',
        }}
        sx={{
          zIndex: (theme) => theme.zIndex.modal + 100,
          '& .MuiPopover-paper': {
            maxWidth: 350,
            boxShadow: theme.shadows[8]
          }
        }}
      >
        {selectedNode && (
          <Card sx={{ border: 'none', boxShadow: 'none' }}>
            <CardContent sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    backgroundColor: getNodeColor(theme, selectedNode.type),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: theme.palette.background.paper
                  }}
                >
                  {React.createElement(getNodeIcon(selectedNode.type), { fontSize: 'small' })}
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1.1rem' }}>
                    {selectedNode.label}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ textTransform: 'capitalize' }}>
                    {selectedNode.type === 'cve' ? 'Common Vulnerability & Exposure' :
                     selectedNode.type === 'vulnerability' ? 'Security Finding' :
                     selectedNode.type === 'instance' ? 'EC2 Instance' :
                     selectedNode.type === 'public_instance' ? 'Public Affected Instance' :
                     selectedNode.type === 'lateral_target' ? 'Lateral Movement Target' :
                     selectedNode.type === 'network' ? 'Network Interface' :
                     selectedNode.type === 'subnet' ? 'VPC Subnet' :
                     selectedNode.type === 'external' ? 'External IP Address' :
                     selectedNode.type === 'external_combined' ? 'Combined External IPs' :
                     selectedNode.type === 'more' ? 'More Items Available' :
                     'Security Entity'}
                  </Typography>
                </Box>
              </Box>
              
              {selectedNode.severity && (
                <Box sx={{ mb: 2 }}>
                  <Chip
                    label={selectedNode.severity.toUpperCase()}
                    color={selectedNode.severity === 'critical' ? 'error' : 
                           selectedNode.severity === 'high' ? 'warning' :
                           selectedNode.severity === 'medium' ? 'info' : 'success'}
                    size="small"
                    sx={{ fontWeight: 600 }}
                  />
                </Box>
              )}
              
              <Typography variant="body2" sx={{ mt: 1, lineHeight: 1.5 }}>
                {selectedNode.details || 
                 (selectedNode.type === 'cve' ? 'Common Vulnerability and Exposure entry' :
                  selectedNode.type === 'vulnerability' ? 'Security vulnerability finding' :
                  selectedNode.type === 'instance' ? 'Amazon EC2 compute instance' :
                  selectedNode.type === 'public_instance' ? 'CVE-affected instance with external access' :
                  selectedNode.type === 'lateral_target' ? 'Instance reachable via lateral movement' :
                  selectedNode.type === 'network' ? 'Virtual network interface' :
                  selectedNode.type === 'subnet' ? 'Virtual private cloud subnet' :
                  selectedNode.type === 'external' ? 'External IP address connection' :
                  selectedNode.type === 'external_combined' ? 'Click to expand and view individual external IP addresses' :
                  selectedNode.type === 'more' ? 'More items available in this layer' :
                  'Security graph entity')}
              </Typography>
              
              <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block', fontFamily: 'monospace' }}>
                ID: {selectedNode.id}
              </Typography>
            </CardContent>
          </Card>
        )}
      </Popover>
    </Box>
  );
}