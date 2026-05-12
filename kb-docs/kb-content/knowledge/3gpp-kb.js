const express = require('express');
const fs = require('fs');

class ThreeGPPKnowledgeBase {
    constructor() {
        this.app = express();
        this.port = 8098;
        this.knowledgeBase = this.initializeKnowledgeBase();
        this.setupMiddleware();
        this.setupRoutes();
    }

    initializeKnowledgeBase() {
        return {
            specifications: {
                'TS 23.501': {
                    title: 'System architecture for the 5G System (5GS)',
                    release: 'Rel-17',
                    category: 'Architecture',
                    procedures: ['Registration', 'Deregistration', 'Service Request', 'PDU Session Establishment'],
                    networkFunctions: ['AMF', 'SMF', 'UPF', 'AUSF', 'UDM', 'PCF', 'NRF', 'NSSF', 'UDR'],
                    keyFeatures: ['Network Slicing', 'Service Based Architecture', 'Control/User Plane Separation']
                },
                'TS 23.502': {
                    title: 'Procedures for the 5G System (5GS)',
                    release: 'Rel-17',
                    category: 'Procedures',
                    procedures: ['Initial Registration', 'Mobility Registration Update', 'PDU Session Establishment', 'Handover'],
                    flows: ['UE Registration', 'Service Request', 'PDU Session Management', 'Mobility Management']
                },
                'TS 29.500': {
                    title: 'Technical Realization of Service Based Architecture',
                    release: 'Rel-17',
                    category: 'Technical Implementation',
                    interfaces: ['Namf', 'Nsmf', 'Nausf', 'Nudm', 'Npcf', 'Nnrf', 'Nnssf', 'Nudr'],
                    protocols: ['HTTP/2', 'JSON', 'OAuth 2.0', 'TLS 1.3']
                },
                'TS 38.401': {
                    title: 'NG-RAN; Architecture description',
                    release: 'Rel-17',
                    category: 'RAN Architecture',
                    interfaces: ['NG', 'Xn', 'F1', 'E1'],
                    nodes: ['gNB', 'ng-eNB', 'gNB-CU', 'gNB-DU']
                }
            },
            procedures: {
                'UE_REGISTRATION': {
                    standard: 'TS 23.502',
                    steps: [
                        'UE sends Registration Request to AMF',
                        'AMF performs authentication via AUSF',
                        'AMF retrieves subscription data from UDM',
                        'AMF completes registration and sends Registration Accept'
                    ],
                    interfaces: ['N1', 'N8', 'N10', 'N12'],
                    mandatory_ies: ['5G-GUTI', 'Registration Type', 'UE Security Capability']
                },
                'PDU_SESSION_ESTABLISHMENT': {
                    standard: 'TS 23.502',
                    steps: [
                        'UE sends PDU Session Establishment Request',
                        'AMF selects SMF and forwards request',
                        'SMF selects UPF and establishes session',
                        'SMF sends PDU Session Establishment Accept'
                    ],
                    interfaces: ['N1', 'N11', 'N4'],
                    mandatory_ies: ['PDU Session ID', 'DNN', 'S-NSSAI']
                },
                'HANDOVER': {
                    standard: 'TS 23.502',
                    steps: [
                        'Source gNB makes handover decision',
                        'Source gNB sends Handover Required to AMF',
                        'AMF sends Handover Request to Target gNB',
                        'Target gNB sends Handover Request Acknowledge'
                    ],
                    interfaces: ['N2', 'Xn'],
                    mandatory_ies: ['Target ID', 'Cause', 'Source to Target Container']
                }
            },
            networkSlicing: {
                'eMBB': {
                    sst: 1,
                    characteristics: 'Enhanced Mobile Broadband',
                    useCases: ['Ultra HD video', 'AR/VR', 'Cloud gaming'],
                    requirements: { latency: '< 20ms', throughput: '> 1Gbps' }
                },
                'URLLC': {
                    sst: 2,
                    characteristics: 'Ultra-Reliable Low Latency Communications',
                    useCases: ['Industrial automation', 'Autonomous vehicles', 'Remote surgery'],
                    requirements: { latency: '< 1ms', reliability: '99.999%' }
                },
                'mMTC': {
                    sst: 3,
                    characteristics: 'Massive Machine Type Communications',
                    useCases: ['IoT sensors', 'Smart city', 'Agriculture monitoring'],
                    requirements: { density: '1M devices/km²', battery: '> 10 years' }
                }
            }
        };
    }

    setupMiddleware() {
        this.app.use(express.json());
        this.app.use((req, res, next) => {
            console.log(`[3GPP-KB] ${req.method} ${req.path}`);
            next();
        });
    }

    setupRoutes() {
        // Search Knowledge Base
        this.app.get('/search', (req, res) => {
            const { query, category } = req.query;
            const results = this.searchKnowledgeBase(query, category);
            res.json({
                query,
                category,
                results,
                total: results.length,
                timestamp: new Date().toISOString()
            });
        });

        // Get Specification Details
        this.app.get('/specification/:specId', (req, res) => {
            const spec = this.knowledgeBase.specifications[req.params.specId];
            if (!spec) {
                return res.status(404).json({ error: 'Specification not found' });
            }
            res.json({
                specificationId: req.params.specId,
                ...spec,
                timestamp: new Date().toISOString()
            });
        });

        // Get Procedure Details
        this.app.get('/procedure/:procedureId', (req, res) => {
            const procedure = this.knowledgeBase.procedures[req.params.procedureId];
            if (!procedure) {
                return res.status(404).json({ error: 'Procedure not found' });
            }
            res.json({
                procedureId: req.params.procedureId,
                ...procedure,
                timestamp: new Date().toISOString()
            });
        });

        // Validate Compliance
        this.app.post('/validate', (req, res) => {
            const { procedure, parameters } = req.body;
            const validation = this.validateCompliance(procedure, parameters);
            res.json({
                procedure,
                validation,
                timestamp: new Date().toISOString()
            });
        });

        // Get Network Slice Information
        this.app.get('/slice/:sliceType', (req, res) => {
            const slice = this.knowledgeBase.networkSlicing[req.params.sliceType];
            if (!slice) {
                return res.status(404).json({ error: 'Slice type not found' });
            }
            res.json({
                sliceType: req.params.sliceType,
                ...slice,
                timestamp: new Date().toISOString()
            });
        });

        // List All Specifications
        this.app.get('/specifications', (req, res) => {
            res.json({
                specifications: Object.keys(this.knowledgeBase.specifications).map(key => ({
                    id: key,
                    title: this.knowledgeBase.specifications[key].title,
                    release: this.knowledgeBase.specifications[key].release,
                    category: this.knowledgeBase.specifications[key].category
                })),
                total: Object.keys(this.knowledgeBase.specifications).length,
                timestamp: new Date().toISOString()
            });
        });

        // Health Check
        this.app.get('/health', (req, res) => {
            res.json({
                service: '3GPP Knowledge Base',
                status: 'healthy',
                specifications: Object.keys(this.knowledgeBase.specifications).length,
                procedures: Object.keys(this.knowledgeBase.procedures).length,
                timestamp: new Date().toISOString()
            });
        });
    }

    searchKnowledgeBase(query, category) {
        const results = [];
        const searchTerm = query.toLowerCase();

        // Search specifications
        Object.entries(this.knowledgeBase.specifications).forEach(([id, spec]) => {
            if (!category || category === 'specifications') {
                if (spec.title.toLowerCase().includes(searchTerm) || 
                    spec.category.toLowerCase().includes(searchTerm) ||
                    id.toLowerCase().includes(searchTerm)) {
                    results.push({
                        type: 'specification',
                        id,
                        title: spec.title,
                        category: spec.category,
                        relevance: this.calculateRelevance(searchTerm, spec)
                    });
                }
            }
        });

        // Search procedures
        Object.entries(this.knowledgeBase.procedures).forEach(([id, proc]) => {
            if (!category || category === 'procedures') {
                if (id.toLowerCase().includes(searchTerm) ||
                    proc.standard.toLowerCase().includes(searchTerm)) {
                    results.push({
                        type: 'procedure',
                        id,
                        standard: proc.standard,
                        steps: proc.steps.length,
                        relevance: this.calculateRelevance(searchTerm, proc)
                    });
                }
            }
        });

        return results.sort((a, b) => b.relevance - a.relevance);
    }

    calculateRelevance(searchTerm, item) {
        let score = 0;
        const text = JSON.stringify(item).toLowerCase();
        const matches = (text.match(new RegExp(searchTerm, 'g')) || []).length;
        return matches;
    }

    validateCompliance(procedure, parameters) {
        const procDef = this.knowledgeBase.procedures[procedure];
        if (!procDef) {
            return {
                compliant: false,
                errors: ['Unknown procedure'],
                standard: 'N/A'
            };
        }

        const errors = [];
        const warnings = [];

        // Check mandatory IEs
        if (procDef.mandatory_ies) {
            procDef.mandatory_ies.forEach(ie => {
                if (!parameters[ie]) {
                    errors.push(`Missing mandatory IE: ${ie}`);
                }
            });
        }

        // Validate specific parameters
        if (procedure === 'PDU_SESSION_ESTABLISHMENT') {
            if (parameters['PDU Session ID'] && (parameters['PDU Session ID'] < 1 || parameters['PDU Session ID'] > 15)) {
                errors.push('PDU Session ID must be between 1-15');
            }
        }

        return {
            compliant: errors.length === 0,
            errors,
            warnings,
            standard: procDef.standard,
            checkedIEs: procDef.mandatory_ies || []
        };
    }

    start() {
        this.app.listen(this.port, () => {
            console.log(`📚 3GPP Knowledge Base running on port ${this.port}`);
            console.log(`📋 ${Object.keys(this.knowledgeBase.specifications).length} specifications loaded`);
            console.log(`🔄 ${Object.keys(this.knowledgeBase.procedures).length} procedures available`);
        });
    }
}

const knowledgeBase = new ThreeGPPKnowledgeBase();
knowledgeBase.start();

module.exports = ThreeGPPKnowledgeBase;
