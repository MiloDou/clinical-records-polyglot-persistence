# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

delegated: React with TypeScript for the client and CSS for the visual system, based on the user's accepted recommendation. This phase builds the frontend only; the server/API and persistence adapters are not present in the repository.

## Users

Staff who provide or administer care across a hospital, a small dental clinic, a clinical laboratory, and a pediatric medical center. The project brief describes the workflows and operating context for these institutions; detailed role permissions remain to be confirmed during backend design.

## Product Purpose

Provide a shared client-server application for consulting and maintaining patient histories across four independent medical institutions. The target system must support new and existing patients while persisting each institution's data in its assigned database engine.

## Positioning

The same clinical workflows and interface serve all four institutions. After authentication, the server routes each user's operations to the institution's database through a common hexagonal architecture, keeping the business rules independent of the storage engine.

## Operating Context

Users need to search for patients, review their histories, register new histories, and maintain clinical records. The hospital emphasizes transaction integrity for appointments, diagnoses, and treatments. The dental clinic prioritizes quick service through its secretaries. The laboratory handles result structures that vary by examination. The pediatric center records repeated growth measurements and vaccination histories.

## Capabilities and Constraints

- Final project scope covers hospital general, dental clinic, clinical laboratory, and pediatric medical center.
- The requirements assign a distinct database engine to each institution, using PostgreSQL, MySQL, MongoDB, and Firebase once each. The final assignment is still open.
- Required operations include patient registration and search, history review and maintenance, appointments, consultations, diagnoses, treatments, prescriptions, laboratory examinations and results, pediatric growth and vaccination records, and archival/deactivation of histories.
- The authenticated user's institution determines server-side database routing. The interface must remain consistent across database engines.
- MongoDB and Firebase need explicit document-modeling decisions, including which data is embedded and which is referenced.
- The user selected a frontend-only phase with interface screens and empty states. Do not seed or persist mock clinical records. Until an API exists, clearly indicate when a save or search cannot be completed.
- The delivered reference PDF for Entrega I covers hospital and pediatrics; the project requirements PDF defines the complete four-institution scope.

## Brand Commitments

The user specified a Soviet editorial visual direction inspired by the Sputnik 3 era and the provided image references. The opening page makes the user's political statement explicit: universal public healthcare is a right. The workbench remains calm, readable, and respectful. The existing `docs/frontend/guia-estilo-sovietico-sputnik3.md` is the visual authority for the graphic language; it is inspiration, not a claim that the interface reproduces historical Sputnik technology.

## Evidence on Hand

- Project requirements: `../Proyecto final bases - requerimientos .pdf`.
- Submitted Entrega I reference: `../Documents/Entrega_01_la_entregada.pdf`.
- Visual system: `docs/frontend/guia-estilo-sovietico-sputnik3.md`.
- No existing application code, API, authentication provider, database connection, or real patient data is present in this repository.

## Product Principles

1. Keep patient and clinical information easy to scan and private.
2. Preserve consistent workflows across all database engines.
3. Make each institution's distinct work visible without fragmenting the shared interface.
4. Do not imply that an action succeeded when no server is connected.
5. Keep institutional routing, authorization, validation, and persistence responsibilities on the server.
