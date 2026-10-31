# PrivLens: Technical Privacy Evidence & Metadata Inventory Report

> **IMPORTANT LEGAL BOUNDARY & EVIDENCE DISCLAIMER**  
> This report contains *technical evidence* discovered by automated heuristic profiling. 
> It **does NOT** constitute a legal compliance determination, **does NOT** infer GDPR/CCPA lawful basis, 
> and **does NOT** deduce universal data transfer flows. Findings are strictly formulated 
> as an evidence checklist for human privacy officer review.

## 1. Executive Technical Summary

| Metric | Count |
| :--- | :--- |
| **Total Fields Scanned** | `44` |
| **Candidate PII Fields Discovered** | `31` |
| **Non-PII Technical Columns** | `13` |
| **Identified Governance & Evidence Gaps** | `15` |

### Distribution Across 5 Predefined Data Classes

| Predefined Data Class | Candidate Fields Discovered |
| :--- | :--- |
| **Contact information** | 4 |
| **Financial information** | 8 |
| **Government identifiers** | 7 |
| **Location / address** | 6 |
| **Personal identity** | 6 |

## 2. Structured Technical Evidence Inventory

| Target Field | Discovered Class | Confidence | Declared Purpose | Retention Period | Governance Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `customer_signups.csv` : **customer_name** | Personal identity | `100%` | Customer Order Fulfillment & Shipping | 36 months (Account Deletion) | `ACTIVE` |
| `customer_signups.csv` : **email_address** | Contact information | `100%` | Customer Order Fulfillment & Shipping | 36 months (Account Deletion) | `ACTIVE` |
| `customer_signups.csv` : **phone_number** | Contact information | `100%` | Customer Order Fulfillment & Shipping | 24 months (Order Completion) | `ACTIVE` |
| `customer_signups.csv` : **date_of_birth** | Personal identity | `100%` | *(Missing Purpose)* | *(Missing Retention)* | `UNREGISTERED` |
| `customer_signups.csv` : **gender** | Personal identity | `100%` | *(Missing Purpose)* | 12 months (Account Review) | `UNLINKED_PURPOSE` |
| `customer_signups.csv` : **residential_address** | Location / address | `100%` | Customer Order Fulfillment & Shipping | *(Missing Retention)* | `INCOMPLETE` |
| `customer_signups.csv` : **pin_code** | Location / address | `100%` | Customer Order Fulfillment & Shipping | 36 months (Account Deletion) | `ACTIVE` |
| `digital_payments_log.csv` : **bank_account_number** | Financial information | `100%` | Payment Processing & Financial Ledger | 84 months (Financial Year End) | `ACTIVE` |
| `digital_payments_log.csv` : **ifsc_code** | Financial information | `100%` | Payment Processing & Financial Ledger | 84 months (Financial Year End) | `ACTIVE` |
| `digital_payments_log.csv` : **card_number** | Financial information | `100%` | *(Missing Purpose)* | 24 months (Card Expiration) | `UNLINKED_PURPOSE` |
| `digital_payments_log.csv` : **upi_id** | Financial information | `100%` | *(Missing Purpose)* | *(Missing Retention)* | `UNREGISTERED` |
| `kyc_verification_records.csv` : **aadhaar_number** | Government identifiers | `100%` | Statutory KYC & Customer Verification | 60 months (Statutory Audit Window) | `ACTIVE` |
| `kyc_verification_records.csv` : **pan_number** | Government identifiers | `100%` | Statutory KYC & Customer Verification | 60 months (Statutory Audit Window) | `ACTIVE` |
| `kyc_verification_records.csv` : **passport_number** | Government identifiers | `100%` | Statutory KYC & Customer Verification | *(Missing Retention)* | `INCOMPLETE` |
| `kyc_verification_records.csv` : **voter_id** | Government identifiers | `100%` | *(Missing Purpose)* | *(Missing Retention)* | `UNREGISTERED` |
| `kyc_verification_records.csv` : **driving_licence** | Government identifiers | `100%` | *(Missing Purpose)* | *(Missing Retention)* | `UNREGISTERED` |
| `enterprise_data.db` (`employees`) : **employee_name** | Personal identity | `100%` | Employee Payroll & Statutory Benefits | 84 months (Termination of Employment) | `ACTIVE` |
| `enterprise_data.db` (`employees`) : **age** | Personal identity | `100%` | Employee Payroll & Statutory Benefits | 84 months (Termination of Employment) | `ACTIVE` |
| `enterprise_data.db` (`employees`) : **pan_card** | Government identifiers | `100%` | Employee Payroll & Statutory Benefits | 84 months (Statutory Tax Filing) | `ACTIVE` |
| `enterprise_data.db` (`employees`) : **salary_account_no** | Financial information | `100%` | Employee Payroll & Statutory Benefits | 84 months (Termination of Employment) | `ACTIVE` |
| `enterprise_data.db` (`employees`) : **bank_ifsc** | Financial information | `100%` | Employee Payroll & Statutory Benefits | 84 months (Termination of Employment) | `ACTIVE` |
| `enterprise_data.db` (`delivery_dispatch`) : **delivery_address** | Location / address | `100%` | Customer Order Fulfillment & Shipping | 12 months (Delivery Confirmation) | `ACTIVE` |
| `enterprise_data.db` (`delivery_dispatch`) : **postal_pin** | Location / address | `100%` | Customer Order Fulfillment & Shipping | 12 months (Delivery Confirmation) | `ACTIVE` |
| `enterprise_data.db` (`delivery_dispatch`) : **geo_coords** | Location / address | `100%` | Customer Order Fulfillment & Shipping | *(Missing Retention)* | `INCOMPLETE` |
| `enterprise_data.db` (`delivery_dispatch`) : **order_upi** | Financial information | `100%` | Payment Processing & Financial Ledger | 24 months (Dispute Window) | `ACTIVE` |
| `enterprise_data.db` (`legacy_unindexed_vault`) : **aadhaar_card** | Government identifiers | `100%` | *(Missing Purpose)* | *(Missing Retention)* | `UNREGISTERED` |
| `enterprise_data.db` (`legacy_unindexed_vault`) : **caller_phone** | Contact information | `100%` | *(Missing Purpose)* | *(Missing Retention)* | `UNREGISTERED` |
| `enterprise_data.db` (`legacy_unindexed_vault`) : **contact_email** | Contact information | `100%` | *(Missing Purpose)* | *(Missing Retention)* | `UNREGISTERED` |
| `enterprise_data.db` (`legacy_unindexed_vault`) : **card_number** | Financial information | `100%` | *(Missing Purpose)* | *(Missing Retention)* | `UNREGISTERED` |
| `enterprise_data.db` (`legacy_unindexed_vault`) : **birth_date** | Personal identity | `100%` | *(Missing Purpose)* | *(Missing Retention)* | `UNREGISTERED` |
| `enterprise_data.db` (`legacy_unindexed_vault`) : **geo_coordinates** | Location / address | `100%` | *(Missing Purpose)* | *(Missing Retention)* | `UNREGISTERED` |

## 3. Evidence Gaps & Missing Metadata Action Checklist

| Severity | Target Field | Gap Type | Description & Human Recommendation |
| :--- | :--- | :--- | :--- |
| **CRITICAL** | `customer_signups.csv::date_of_birth` | `UNREGISTERED_SHADOW_DATA` | **Unregistered Candidate PII in customer_signups.csv**: Field 'date_of_birth' was identified as candidate personal data (Personal identity, confidence: 100%) across 150 records, but has NO entry in the governance registry.<br>↳ *Action:* Human Review Required: Consult data owner to verify business necessity. If legitimate, register processing purpose and retention policy in RoPA. If obsolete, initiate data minimization or decommissioning. |
| **CRITICAL** | `digital_payments_log.csv::upi_id` | `UNREGISTERED_SHADOW_DATA` | **Unregistered Candidate PII in digital_payments_log.csv**: Field 'upi_id' was identified as candidate personal data (Financial information, confidence: 100%) across 100 records, but has NO entry in the governance registry.<br>↳ *Action:* Human Review Required: Consult data owner to verify business necessity. If legitimate, register processing purpose and retention policy in RoPA. If obsolete, initiate data minimization or decommissioning. |
| **CRITICAL** | `kyc_verification_records.csv::voter_id` | `UNREGISTERED_SHADOW_DATA` | **Unregistered Candidate PII in kyc_verification_records.csv**: Field 'voter_id' was identified as candidate personal data (Government identifiers, confidence: 100%) across 120 records, but has NO entry in the governance registry.<br>↳ *Action:* Human Review Required: Consult data owner to verify business necessity. If legitimate, register processing purpose and retention policy in RoPA. If obsolete, initiate data minimization or decommissioning. |
| **CRITICAL** | `kyc_verification_records.csv::driving_licence` | `UNREGISTERED_SHADOW_DATA` | **Unregistered Candidate PII in kyc_verification_records.csv**: Field 'driving_licence' was identified as candidate personal data (Government identifiers, confidence: 100%) across 120 records, but has NO entry in the governance registry.<br>↳ *Action:* Human Review Required: Consult data owner to verify business necessity. If legitimate, register processing purpose and retention policy in RoPA. If obsolete, initiate data minimization or decommissioning. |
| **CRITICAL** | `enterprise_data.db:legacy_unindexed_vault::aadhaar_card` | `UNREGISTERED_SHADOW_DATA` | **Unregistered Candidate PII in enterprise_data.db:legacy_unindexed_vault**: Field 'aadhaar_card' was identified as candidate personal data (Government identifiers, confidence: 100%) across 70 records, but has NO entry in the governance registry.<br>↳ *Action:* Human Review Required: Consult data owner to verify business necessity. If legitimate, register processing purpose and retention policy in RoPA. If obsolete, initiate data minimization or decommissioning. |
| **CRITICAL** | `enterprise_data.db:legacy_unindexed_vault::caller_phone` | `UNREGISTERED_SHADOW_DATA` | **Unregistered Candidate PII in enterprise_data.db:legacy_unindexed_vault**: Field 'caller_phone' was identified as candidate personal data (Contact information, confidence: 100%) across 70 records, but has NO entry in the governance registry.<br>↳ *Action:* Human Review Required: Consult data owner to verify business necessity. If legitimate, register processing purpose and retention policy in RoPA. If obsolete, initiate data minimization or decommissioning. |
| **CRITICAL** | `enterprise_data.db:legacy_unindexed_vault::contact_email` | `UNREGISTERED_SHADOW_DATA` | **Unregistered Candidate PII in enterprise_data.db:legacy_unindexed_vault**: Field 'contact_email' was identified as candidate personal data (Contact information, confidence: 100%) across 70 records, but has NO entry in the governance registry.<br>↳ *Action:* Human Review Required: Consult data owner to verify business necessity. If legitimate, register processing purpose and retention policy in RoPA. If obsolete, initiate data minimization or decommissioning. |
| **CRITICAL** | `enterprise_data.db:legacy_unindexed_vault::card_number` | `UNREGISTERED_SHADOW_DATA` | **Unregistered Candidate PII in enterprise_data.db:legacy_unindexed_vault**: Field 'card_number' was identified as candidate personal data (Financial information, confidence: 100%) across 70 records, but has NO entry in the governance registry.<br>↳ *Action:* Human Review Required: Consult data owner to verify business necessity. If legitimate, register processing purpose and retention policy in RoPA. If obsolete, initiate data minimization or decommissioning. |
| **CRITICAL** | `enterprise_data.db:legacy_unindexed_vault::birth_date` | `UNREGISTERED_SHADOW_DATA` | **Unregistered Candidate PII in enterprise_data.db:legacy_unindexed_vault**: Field 'birth_date' was identified as candidate personal data (Personal identity, confidence: 100%) across 70 records, but has NO entry in the governance registry.<br>↳ *Action:* Human Review Required: Consult data owner to verify business necessity. If legitimate, register processing purpose and retention policy in RoPA. If obsolete, initiate data minimization or decommissioning. |
| **CRITICAL** | `enterprise_data.db:legacy_unindexed_vault::geo_coordinates` | `UNREGISTERED_SHADOW_DATA` | **Unregistered Candidate PII in enterprise_data.db:legacy_unindexed_vault**: Field 'geo_coordinates' was identified as candidate personal data (Location / address, confidence: 100%) across 70 records, but has NO entry in the governance registry.<br>↳ *Action:* Human Review Required: Consult data owner to verify business necessity. If legitimate, register processing purpose and retention policy in RoPA. If obsolete, initiate data minimization or decommissioning. |
| **HIGH** | `customer_signups.csv::gender` | `MISSING_PURPOSE` | **Missing Declared Purpose for gender**: Field 'gender' is registered under customer_signups.csv but has no declared business processing purpose.<br>↳ *Action:* Privacy Steward Action: Assign and validate a declared business purpose prior to lawful processing verification. |
| **HIGH** | `customer_signups.csv::residential_address` | `MISSING_RETENTION` | **Missing Retention Schedule for residential_address**: Field 'residential_address' contains candidate personal data without a defined retention limit or deletion trigger.<br>↳ *Action:* Data Governance Action: Formulate data retention schedule and disposal trigger in accordance with corporate data retention policy. |
| **HIGH** | `digital_payments_log.csv::card_number` | `MISSING_PURPOSE` | **Missing Declared Purpose for card_number**: Field 'card_number' is registered under digital_payments_log.csv but has no declared business processing purpose.<br>↳ *Action:* Privacy Steward Action: Assign and validate a declared business purpose prior to lawful processing verification. |
| **HIGH** | `kyc_verification_records.csv::passport_number` | `MISSING_RETENTION` | **Missing Retention Schedule for passport_number**: Field 'passport_number' contains candidate personal data without a defined retention limit or deletion trigger.<br>↳ *Action:* Data Governance Action: Formulate data retention schedule and disposal trigger in accordance with corporate data retention policy. |
| **HIGH** | `enterprise_data.db:delivery_dispatch::geo_coords` | `MISSING_RETENTION` | **Missing Retention Schedule for geo_coords**: Field 'geo_coords' contains candidate personal data without a defined retention limit or deletion trigger.<br>↳ *Action:* Data Governance Action: Formulate data retention schedule and disposal trigger in accordance with corporate data retention policy. |
