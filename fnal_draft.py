from agents import Agent, ModelSettings, function_tool, trace
import asyncio
from agents import Runner
import json
import sys
import os
from concurrent.futures import ThreadPoolExecutor
import time
from pydantic import BaseModel
#from agents.extensions.visualization import draw_graph
import pandas as pd
import mysql.connector
from mysql.connector import Error


#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#from common.functions import query_open_ai, table_desc_loader, extract_inside_brackets, prompt_template, prompt_template_layer2, sql_prompt_template, query_open_ai_new, query_open_ai_newer # Hook this up later if needed
#from vector_db import query_vector_db







import streamlit as st




import base64
import urllib.request


df_result_set=None

FILE_ID = "16YDf3yQ1EMh2B8fx7vVlFfKpTKooKX_P"
DIRECT_URL = f"https://drive.google.com/uc?id={FILE_ID}"

def image_url_to_base64(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        data = response.read()
    return base64.b64encode(data).decode("utf-8")

b64 = image_url_to_base64(DIRECT_URL)
st.markdown(
    f"""
    <style>
    /* Background */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{b64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        min-height: 100vh;
    }}

    /* Make main content transparent if you want */
    .block-container {{
        background: transparent;
        padding-top: 72px; /* space for fixed title */
    }}

    /* Optional: make Streamlit's default header transparent */
    [data-testid="stHeader"] {{
        background: transparent;
    }}

    /* Fixed, centered title on TOP of everything */
    .fixed-title {{
        position: fixed;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        text-align: center;
        padding: 12px 16px;
        font-size: 28px;
        font-weight: 700;
        color: white;
        background: rgba(0,0,200,0.35); /* contrast over any background */
        z-index: 99999;               /* <-- keep this very high */
        pointer-events: none;          /* clicks pass through */
    }}
    </style>

    <div class="fixed-title">PMI's Segment Lens Pilot</div>
    """,
    unsafe_allow_html=True,
)



st.markdown(
    """
    <style>
    .fixed-title {
        position: fixed;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgb(14, 17, 23);
        width: 100%;
        text-align: center;
        padding: 10px;
        font-size: 28px;
        font-weight: bold;
        z-index: 1000;
        border-bottom: 1px solid #ddd;
    }
    </style>
    <div class="fixed-title">🚀 PMI's Segment Lens Pilot</div>
    """,
    unsafe_allow_html=True
)






# Just to prove it scrolls
#for i in range(50):
#    st.write(f"Row {i+1}")

# Sticky input bar (stays fixed at bottom)
user_text = st.chat_input("Type here...")  # this bar is fixed to bottom

#if user_text:
#    st.info(f"### Q: {user_text}")







file_path_db = 'table_dict.json'
with open(file_path_db, 'r', encoding='utf-8') as file:
    db_dict = json.load(file)

class table_list(BaseModel):
    tables: list[str]

class sql_output_quality_checker(BaseModel):
    answers_users_question:bool
    explanation:str


class sql_generation_format(BaseModel):
    sql_query:str
    explanation:str


@function_tool  
async def run_sql(query: str) -> list[dict]:  
#async def run_sql(query: str) -> pd.DataFrame:
    global df_result_set
  
           
    conn = mysql.connector.connect(
        host="localhost",      # or your MySQL server IP
        user="root",  # replace with your MySQL username
        password="fiRiam95", 
        database="db_l3_merge"
        )
    cursor = conn.cursor()
    cursor.execute(query)

    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]

    df = pd.DataFrame(rows, columns=col_names)

    cursor.close()
    conn.close()


    df_result_set = df
    #return df
    # convert DataFrame to JSON-serializable list of dicts
    return df.to_dict(orient="records")



metadata_sql= Agent(
    name="metadata SQL agent",
    instructions="""A user has asked a question regarding the metadata of our comapany's database, use the table information below to answer their question. If answering their question requires running some SQL query then hand off to the sql_analysis_agent
    
    Here is the database information:
    
    {"table name":"ACTIVITY",
"text":"This table aggregates detailed customer engagement metrics for Philip Morris International, uniquely keyed by persona_identifier. It logs diverse activities including lending order flags, total case counts with inbound/outbound origins, and channel-specific case volumes (CSC, website, chat, email), alongside case statuses (closed, new, open) and varied case types such as order management, product issues, and program support (conversion, retention, MyIQOS) as well as customer inquiries. Additionally, it tracks a spectrum of loyalty actions—from refer-a-friend and device linkage to IQOS logins and loyalty surveys—and records comprehensive order metrics (total, discounted, normal, returns, replacements, accessories, heets, kit) paired with granular web event data (form logins, add-to-cart, product views, purchases, diverse page views, and referrer details) plus referral counts. This dense synthesis of transactional, service, and digital behavior data supports in-depth analyses of customer interactions and operational performance."},

{"table name":"campaign",
"text":"This table encapsulates detailed marketing campaign data for PMI, where each campaign is uniquely identified by attributes such as campaign_identifier and campaign_name. It includes a narrative description in campaign_description, geographic targeting via campaign_country, and timing details using campaign_start_time, campaign_end_time, and campaign_create_time to chronicle the campaign lifecycle. The global_campaign_flag indicates whether the campaign has a worldwide scope, while campaign_partner records associated external or internal partners. This schema supports analytical queries for campaign effectiveness, scheduling, and partner performance, crucial for evaluating multi-regional strategies including those for devices like IQOS and ILLUMA."},

{"table name":"campaign_activity",
"text":"This table details PMI's marketing campaign activities, uniquely identified by campaign_activity_identifier, and links to broader strategic campaigns via campaign_identifier. It records critical time markers in text format—campaign_activity_start_time and campaign_activity_end_time—for tracking the campaign lifecycle. The table categorizes campaigns by channel, category, and customer journey state through campaign_activity_channel, campaign_activity_category, and campaign_activity_journey_state, which support multifaceted audience engagement analysis. Supplementary columns like campaign_activity_name, campaign_activity_description, and campaign_activity_frequency provide insights into the campaign's branding, messaging, and periodicity, while campaign_activity_business_objective and campaign_activity_product indicate the underlying business goals and association with specific PMI products."},

{"table name":"campaign_contact",
"text":"This table captures a comprehensive history of campaign contacts for PMI, recording detailed interaction data key to evaluating outreach effectiveness. It uniquely tracks each contact via campaign_id, campaign_name, and campaign_activity_id while storing message content (message_text) and transmission metadata (triggeredsendexternalkey, message_id, send_id). The table supports multi-channel analysis through fields like channel, channel_value, and social_app, supplemented by source_system information to trace origin. Additional attributes such as from_email, from_name, and home_country enhance profiling, while identity_type and persona_identifier help align contacts with specific customer segments. Fields like event_date, event_type, and event_identifier, along with reason_not_sent, offer precise audit trails and analytical insights into campaign performance and messaging exceptions."},

{"table name":"campaign_response",
"text":"This table archives historical response data for PMI marketing campaigns, capturing granular details of user engagement and digital interactions. Each response is uniquely identified by event_id and is associated with campaign metadata including campaign_name, campaign_id, campaign_activity, and campaign_activity_name, essential for tracing campaign performance. It records detailed email attributes (emailclient, from_email, send_id), URL specifics (url, url_alias, url_id), and technical data (operatingsystem, browser, device) that facilitate analysis of channel effectiveness and platform behavior. Additional columns such as bounce_category, identity_type, persona_identifier, channel, channel_value, and home_country provide further segmentation for targeting and regulatory compliance, while brand_family links responses to specific PMI product lines. The event_date timestamp supports chronological tracking and trend analyses for strategic marketing insights."},

{"table name":"campaign_taxonomy",
"text":"This table captures detailed metadata for PMI’s marketing campaigns, organizing both outbound and inbound communications into a structured taxonomy that supports campaign analysis and strategic alignment. Key identifiers like campaign_key, promotion_id, and local_action_id uniquely track each campaign, while columns such as scope, communication_direction, and campaign_channel define the reach and direction of interactions. It also delineates channels and consumer touchpoints through fields like outbound_channel, inbound_channel, consumer_entry_point, and platform. Additionally, the table maps customer journeys and promotional milestones using journey_name, journey_activity_name, journey_state, and sequence_type, paired with business-critical metrics from business_objective, timing, and frequency. Other columns such as promotion_value, promotion_benefit, and promotion_type, alongside product_type, product_edition, and product_generation, provide insight into the campaign’s offer details and product associations. This comprehensive schema serves to support semantic queries, detailed campaign performance analytics, and complex NL2SQL mapping requirements."},

{"table name":"case",
"text":"This table encapsulates comprehensive customer care cases for PMI, where each record is uniquely identified by case_identifier. It captures critical classification details using fields such as identity_type, case_record_type_description, case_type, and record_type to differentiate case categories and internal tracking. Key columns like subject, subject_description, and subject_code define the customer issue context, while product-oriented fields including product_family, product_generation, extended_brand_family, and brand_family enable linkage to specific PMI devices and consumables. Operational data such as owner_id, device_codentify, consumable_complaint_reason, case_channel, case_source, and correlation_id facilitate cross-functional case routing and resolution. Date and timeline management is achieved through create_date, closing_date, and latest_update_date, with additional identifiers like appointment_id, case_internal_id, order_id, and persona_identifier enhancing integration across systems and supporting detailed analytics within PMI’s customer care ecosystem."},

{"table name":"consent",
"text":"This table captures consent records related to customer interactions for Philip Morris International, detailing regulatory compliance and user permissions. It includes columns such as terms_and_condition_country and consent_country_extracted that specify the applicable legal jurisdictions, while consent_type and consent_type_extracted classify the nature of the consent. The is_consent_granted field indicates whether permission was granted, and last_consent_modified along with doc_date and doc_version track the temporal aspects and document iterations associated with each consent entry. Unique identifiers like consent_identifier, consent_id, and persona_identifier link these records to individual users and/or profiles, with home_country and identity_type providing additional context about the subject's origin and identification method, thereby supporting critical analyses of legal compliance and customer segmentation."},

{"table name":"consolidated_id",
"text":"This table serves as a centralized mapping repository that links various identity attributes across multiple systems for PMI data integration. It stores key elements such as \"identity_type\" to distinguish between different identification methods, \"source_id\" and \"source_id_raw\" to capture both processed and original identifiers from the originating system, and \"consolidated_id\" functioning as the unified primary identifier. The \"persona_identifier\" aids in associating customer behavioral profiles, while \"source_system\" specifies the origin of data entries, and \"home_country\" provides geographical context. This schema is essential for consolidating fragmented identity data for precise customer segmentation and cross-system analysis in PMI operations."},

{"table name":"control_group",
"text":"This table captures detailed records of control group segments for PMI campaigns, where each entry is uniquely identified by the control_group_id. It logs key temporal markers through submitted_time and created_time, likely representing Unix timestamps for tracking event chronology. The home_country and country columns provide geographical context, while the campaign_id links each control group entry to a specific marketing campaign. The persona_identifier supports segmentation and analysis of user archetypes, enabling nuanced assessment of experimental group behaviors and outcomes in PMI's customer and product engagement studies."},

{"table name":"conversion",
"text":"This table records conversion events where individuals transition partially or fully between market segments, capturing key behavioral shifts for PMI analysis. It documents the customer journey with detailed metadata including the original global and specific questions and answers (original_global_question, original_question, original_answer, original_global_answer) that capture initial engagement. The conversion level and identifiers (conversion_level, conversion_identifier, case_identifier, persona_identifier) uniquely distinguish each event, while fields like survey_id and interaction_id link to broader customer interaction data. Additional details such as source, home_country, product_used_inthepast1week, brand_family, and a timestamp (date) provide context for analyzing trends in consumer conversion behavior and the efficacy of product engagement strategies."},

{"table name":"device",
"text":"This table centrally catalogs detailed PMI device information, capturing product specifics for key devices such as IQOS and ILUMA. Each record is uniquely defined by identification fields like serial_number, device_codentify, and identity_godfather_identifier, while additional product codes (device_product_code, variant_product_code, pack_codentify) ensure precise tracking. Core attributes such as device_description, device_type, device_version, device_color, and device_material_group describe the physical and functional characteristics, whereas columns like condition, grade, and brand_differentiator signal quality and market positioning. Warranty periods (start_of_warranty_date, end_of_warranty_date), purchase_date, registration_device_date, and replacement_date facilitate lifecycle analysis, while status fields (status, disabled, proof_of_purchase_status, trade_in_status, is_for_trial) monitor product lifecycle, usage, and trade-in conditions. Supplementary columns including platform, home_country, identity_type, persona_identifier, component_code, and references to device replacements (replaces, replaced_by) further support operational analytics and relational mappings in customer-product interactions."},

{"table name":"device_action",
"text":"This table captures detailed event logs for device interactions within the PMI ecosystem, uniquely tracking each action via identifiers such as \"id\", \"action_id\", and \"correlation_id\". It records the timing of these interactions with \"device_action_created_date\", \"action_date\", and \"modified_date\", supporting chronological analysis of device events. Columns like \"device_codentify\" and \"asset_id\" link specific devices and assets to recorded activities, while \"persona_identifier\" associates actions with individual user profiles. The \"channel\", \"modified_by\", and \"device_action_created_by\" fields provide context on the operational source and administrating agents behind each action, and \"variant_product_code\" offers insight into product-specific variants potentially including devices like IQOS or ILLUMA. The \"home_country\" field further contextualizes the geographical origin of the action, collectively enabling robust tracking and multi-dimensional analysis of device-related behavior."},

{"table name":"identity",
"text":"This table captures comprehensive identity records for PMI’s registered legal age users (LAU) and legal age smokers (LAS), integrating consent details and opt-in preferences for channels and products such as IQOS. It stores key regulatory and marketing indicators including accepted_privacy_policy, accepted_terms_and_conditions, various opt-in flags (iqos_opt_in, veev_opt_in, call_communication_opt_in, phone_comunication_opt_in, email_comunication_opt_in, global_opt_in, soft_marketing_opt_in_flag), and program-specific markers like care_plus, qure, and qoach. Core identifiers such as identity_unique_identifier and registration_id link users to their demographic (first_name, last_name, date_of_birth, gender, preferred_language) and contact data (email_address, phone_number with phone_country_code_number, residence_state, residence_city, residence_zipcode, residence_address), while timestamps (registration_date, identity_creation_date, lastmodified, last_login_date, opt_in_last_updated_date) trace their activity and profile updates. Additional fields like registration_touchpoint_id, registration_campaign_activity_id, and registration_source_app provide context for user acquisition channels and event tracking, ensuring robust verification, compliance, and segmentation for targeted marketing and operational analysis."},

{"table name":"interaction",
"text":"This table captures detailed transactional events reflecting interactions initiated by Coaches, CSC Agents, or Consumers within the PMI ecosystem, serving as both an operational log and a business audit trail. Key identifiers such as interaction_id, case_id, and contract_id link records across systems, while temporal data captured in date_time ensures precise chronological tracking. Core columns like location_description, location_id, and location_address, along with market_refcode, country_refcode, and state_id, provide geographical context for each event. The table also categorizes interactions via fields such as category, interaction_type_refcode, case_type, channel_refcode, and document_type, and integrates financial dimensions with order_amount and currency. Additional identifiers including external_reference, sap_id, friend_id, correlation_id, and campaign_id facilitate cross-referencing and comprehensive analysis of consumer behavior, vendor performance, and multi-channel engagement. This dense, multifaceted dataset supports business process monitoring, regulatory compliance, and actionable insights into customer and account activities."},

{"table name":"interaction_device",
"text":"This table captures detailed device-related information linked to customer interactions within PMI's ecosystem, crucial for analyzing engagement patterns and regulatory compliance. Each record is anchored by a unique interaction identifier (interaction_id) and incorporates the customer's geographic context via home_country, while persona_identifier associates the interaction with specific customer profiles. The date_time column, recorded as a bigint timestamp, marks the exact interaction moment, and device attributes such as device_id and device_version detail the gadget used. The interaction_type_refcode categorizes the nature of the event, collectively enabling sophisticated tracking of connected device usage in tandem with customer behavior for targeted marketing insights."},

{"table name":"interaction_flavour",
"text":"This table captures detailed records of product consumable interactions, linking key flavor attributes to customer engagements within the PMI ecosystem. Each entry is uniquely identified by an interaction via the `interaction_id` and includes flavor metadata such as `flavour_refname` and `flavour_refcode` necessary for mapping consumable variants used across products like IQOS and ILLUMA. The `interaction_type_refcode` distinguishes different types of consumption events, while `persona_identifier` segments records by user profile. Additional context is provided by `home_country`, indicating the geographical origin of the interaction, and `date_time`, a bigint timestamp that enables chronological analysis of consumption patterns and user behavior."},

{"table name":"interaction_product",
"text":"This table records detailed product data linked to customer interactions across PMI channels, with each entry uniquely identified by the interaction_id. It captures the home_country and platform of the interaction and specifies the product using both product_name and product_id. The interaction_type_refcode classifies the nature of engagement, while consolidated_brand_family groups products under PMI portfolios, potentially including key lines like IQOS or ILLUMA. Additional context is provided by the category and persona_identifier fields, with date_time (as a timestamp) offering a chronological perspective, enabling nuanced analysis of product interactions across regions and consumer segments."},

{"table name":"last_activity",
"text":"This table logs the most recent interaction events for PMI-related entities, capturing key details such as the communication medium via last_activity_channel and the nature of the event through last_activity_action. It records the activity timestamp in last_activity_date (as bigint) and computes temporal recency with days_since_last_activity_date, providing crucial metrics for behavior analysis. The last_activity_table field indicates the originating module or dataset, while persona_identifier serves as the unique key linking to broader customer profiles. Additionally, home_country offers geo-demographic context, making the table valuable for tracking engagement patterns, segmentation, and correlating interactions with PMI device adoption like IQOS or ILLUMA."},

{"table name":"loyalty_activity",
"text":"This table logs detailed consumer loyalty transactions within the PMI loyalty ecosystem, recording every event that earns or redeems points. Each record is uniquely identified by identifiers such as transaction_id, activity_identifier, and action_id, while action_date and action_update_date capture the event timestamps. Core columns include statuspoints and redemptionpoints for tracking point balances, with status_point_expire_date and redemption_point_expire_date denoting expiry thresholds. The table further contextualizes each event with id_type, id_value, related_id_type, and related_value, explaining the linkage between transactions and associated consumer or campaign identifiers. Supplementary fields like action_name, reason, and conversion_amount provide insights into the nature and value of the activity, and local specificity is maintained through site_name, site_id, and home_country, ensuring precise geographic attribution for loyalty behavior analysis."},

{"table name":"loyalty_summary",
"text":"This table encapsulates a detailed snapshot of consumer loyalty accounts at PMI, tracking membership milestones and point transactions crucial for transitioning between loyalty tiers—Bronze, Silver, and Gold. Key columns such as persona_identifier and summary_identifier serve as primary keys linking loyalty records to individual consumer profiles. It records essential dates like join_date and next_points_expiration_date along with metrics including total_redeemed_points, ytd_status_points, and redemption_points to monitor point accrual and usage. Additional columns, including current_tier, next_tier, and status_points_required_for_next_tier, support dynamic tier progression analysis, while site_id and site_name contextualize the loyalty scheme site specifics. Fields like conversion_amount and next_redemption_points_expiration_value provide insights for operational and revenue impact evaluations, making the table vital for strategic customer engagement and loyalty performance analytics."},

{"table name":"nba_action",
"text":"This table defines the next best actions (NBA) recommended for consumers at various stages of their journey, integrating promotion details and action classifications critical for PMI's targeted marketing strategies. It includes descriptive fields such as \"description\", \"promotion_benefit\", \"promotion_value\", \"promotion\", and \"promotion_type\" that encapsulate the nature of each action. Key timing and status columns such as \"active\", \"expiration_date\", \"published\", \"last_modified_date_src\", and \"created_date_src\" ensure accurate tracking of promotion validity and updates. The \"channels\" column outlines communication platforms, while \"priority\" assigns importance levels, and \"typology_name\" with \"typology_id\" classify the specific action group. Unique identifiers \"global_action_id\" and \"action_identifier\" support cross-referencing within PMI's broader ecosystem, and additional fields like \"promotion_id\", \"name\", and \"country\" facilitate segmentation and localization of consumer recommendations."},

{"table name":"order",
"text":"This table captures comprehensive details of legally binding customer orders, encapsulating confirmed requests to buy, sell, deliver, or receive products under specified terms. It records key identifiers such as order_identifier, marketplace_order_id, and order_correlation_id, linking transactions to broader customer interactions. The order’s nature and processing are described through columns like order_channel, order_type, order_status, payment_status, and cancellation_reason_code, while financial elements are detailed with fields including item_price, order_amount, and tradein_discounted_amount. It integrates product-specific information through multiple codes (base_product_code, base_pmi_product_code, variant_pmi_product_code, global_product_code, product_code) and descriptive attributes (base_name_en, variant_name_en, item_description, variant_color_name_en), which are critical for tracking PMI’s product variants such as IQOS or ILLUMA. Additional data such as shipping_method, shipping_date, delivery_tracking, and marketplace_name illuminate fulfillment logistics, and ancillary columns like lending_expiration_time, lending_order_status, and lending_extension_flag support extended service or rental models. Other columns additionally provide context with location details (location_name, location_id, home_country, country), payment_method, platform, and persona_identifier, thereby facilitating integrated analytic queries across customer behavior, market segmentation, and operational workflow management in PMI’s commercial ecosystem."},

{"table name":"order_discount",
"text":"This table captures detailed discount data applied at either the order or item level within PMI transactions, highlighting both promotional coupons and consumer-issued vouchers. It integrates comprehensive product variant details—such as variant_pmi_product_code, variant_product_code, base_product_code, base_pmi_product_code, variant_color_name_en, and variant_brand_family_name—to accurately map discounts to specific device models like IQOS or ILLUMA. Essential identifiers including order_identifier, item_identifier, discount_item_no, and persona_identifier enable precise linkage with customer and order records, while financial columns discount_net and discount_gross quantify discount impacts. Additional fields such as voucher_code, discount_description, and discount_type provide context for the discount origin, and geographical segmentation is addressed through home_country, collectively supporting robust revenue reconciliation and targeted marketing analytics."},

{"table name":"persona_segmentation",
"text":"This table encapsulates detailed segmentation data for PMI customer personas, integrating identifiers and descriptive fields to support precise audience targeting and campaign analytics. Each record is uniquely mapped using the persona’s segmentation identifier (persona_identifier) and segment_id, with segmentation defined across multiple dimensions including geography (segment_country and country), temporal validity (segment_date as a bigint and expired_date as a double), and categorical metadata (segment_channel, segment_category, and segment). The source_segment and source_segment_ref_id columns capture the originating segmentation framework, while segment_description and segment_value provide contextual insights and evaluative data. This dense, multi-faceted segmentation schema enables refined analysis of consumer behavior patterns crucial for tailored marketing strategies and compliance within PMI’s operations."},

{"table name":"rating_value",
"text":"This table captures detailed customer rating responses, integrating temporal, geographical, and survey metadata to support analytical queries on product feedback and market interactions. Key columns include numeric timestamps in submission_date and last_publish_time to record event chronology, and answer – a numerical rating that quantifies customer sentiment. The review_id serves as a unique identifier for each feedback instance, while persona_identifier links to customer identity segments, aiding in demographic or behavioral segmentation. Complementary text fields such as rating_country, home_country, question_label, question_type, and question_id provide contextual details on the origin and nature of the questions posed, enabling nuanced analysis of customer experiences and regulatory profiles relevant to PMI’s targeted markets."},

{"table name":"survey",
"text":"This table aggregates survey data sourced from SFMC, Qualtrics, and Bazaar Voice reviews, capturing both questions and corresponding answers to provide a comprehensive view of customer feedback. It features primary identifiers such as survey_response_id, survey_identifier, question_id, and answer_id that link responses and questions across various digital channels. Key metadata columns like source, url, channel_label, and distribution_channel specify the origin and context of each survey entry, while additional fields (e.g., transaction_identifier, communication_id, touchpoint_identifier, and touchpoint_detail) provide granular insights into the touchpoints and interactions. Temporal markers such as start_date and end_date along with demographic indicators like country, home_country, and consumer_program enable nuanced analysis of campaign performance and consumer behavior within the PMI ecosystem."},

{"table name":"survey_callback",
"text":"This table captures post-survey callback interactions and sentiment analysis for PMI customers, uniquely associating each record with a survey via the `survey_id` and linking service cases through `ticket_id`. It logs key follow-up directives in `next_steps`, while documenting user sentiment through `positive_mentions` and `negative_mentions`, and assessing urgency via the `priority` field. Additional fields such as `home_country` and `country` provide geographic context, whereas `persona_identifier` facilitates customer segmentation. Operational flags like `sentiment_management_performed`, `immediate_watchout`, and `callback_performed` indicate the status and effectiveness of post-survey interventions, ensuring a detailed audit trail for customer support and strategic follow-ups."},
    
    """,
    
)    
    
    
SQL_creator = Agent(
    name="SQL_creator",
    instructions="based in the table selected and user's query, generate an accurate SQL Query",
)  
  

relevance_agent=Agent(
    name="relevance_agent",
    instructions="The user seems to have asked a question which doesn't seem relevant to my job. I need to remind the user that I can assist them in answering questions regarding table descriptions, SQL statments and other metadata information reagarding the company's database"
)  
  
    

table_fetcher= Agent(
    name="table name getter",
    model="o4-mini",
   #model_settings=ModelSettings(tool_choice="SQL_creator"),
    #tools = [SQL_creator.as_tool
    #         (
    #             tool_name="Write_SQL_Query",
    #             tool_description = "Create an SQL query according to the User's query using the relevant tables provided to you."
    #         )
    #         ],
    instructions=("""
                  
The user has asked a question that requires you to choose the relevant tables from the database based on their descriptions. Based on the user's query, choose the relevant tables that must be used to create an SQL query and Pass the choosen table names to SQL_creator agent.    
You must include the choosen table names in the output of your response 
Here are all the table names and their descriptions to choose from:


    {"table name":"ACTIVITY",
"text":"This table aggregates detailed customer engagement metrics for Philip Morris International, uniquely keyed by persona_identifier. It logs diverse activities including lending order flags, total case counts with inbound/outbound origins, and channel-specific case volumes (CSC, website, chat, email), alongside case statuses (closed, new, open) and varied case types such as order management, product issues, and program support (conversion, retention, MyIQOS) as well as customer inquiries. Additionally, it tracks a spectrum of loyalty actions—from refer-a-friend and device linkage to IQOS logins and loyalty surveys—and records comprehensive order metrics (total, discounted, normal, returns, replacements, accessories, heets, kit) paired with granular web event data (form logins, add-to-cart, product views, purchases, diverse page views, and referrer details) plus referral counts. This dense synthesis of transactional, service, and digital behavior data supports in-depth analyses of customer interactions and operational performance."},

{"table name":"campaign",
"text":"This table encapsulates detailed marketing campaign data for PMI, where each campaign is uniquely identified by attributes such as campaign_identifier and campaign_name. It includes a narrative description in campaign_description, geographic targeting via campaign_country, and timing details using campaign_start_time, campaign_end_time, and campaign_create_time to chronicle the campaign lifecycle. The global_campaign_flag indicates whether the campaign has a worldwide scope, while campaign_partner records associated external or internal partners. This schema supports analytical queries for campaign effectiveness, scheduling, and partner performance, crucial for evaluating multi-regional strategies including those for devices like IQOS and ILLUMA."},

{"table name":"campaign_activity",
"text":"This table details PMI's marketing campaign activities, uniquely identified by campaign_activity_identifier, and links to broader strategic campaigns via campaign_identifier. It records critical time markers in text format—campaign_activity_start_time and campaign_activity_end_time—for tracking the campaign lifecycle. The table categorizes campaigns by channel, category, and customer journey state through campaign_activity_channel, campaign_activity_category, and campaign_activity_journey_state, which support multifaceted audience engagement analysis. Supplementary columns like campaign_activity_name, campaign_activity_description, and campaign_activity_frequency provide insights into the campaign's branding, messaging, and periodicity, while campaign_activity_business_objective and campaign_activity_product indicate the underlying business goals and association with specific PMI products."},

{"table name":"campaign_contact",
"text":"This table captures a comprehensive history of campaign contacts for PMI, recording detailed interaction data key to evaluating outreach effectiveness. It uniquely tracks each contact via campaign_id, campaign_name, and campaign_activity_id while storing message content (message_text) and transmission metadata (triggeredsendexternalkey, message_id, send_id). The table supports multi-channel analysis through fields like channel, channel_value, and social_app, supplemented by source_system information to trace origin. Additional attributes such as from_email, from_name, and home_country enhance profiling, while identity_type and persona_identifier help align contacts with specific customer segments. Fields like event_date, event_type, and event_identifier, along with reason_not_sent, offer precise audit trails and analytical insights into campaign performance and messaging exceptions."},

{"table name":"campaign_response",
"text":"This table archives historical response data for PMI marketing campaigns, capturing granular details of user engagement and digital interactions. Each response is uniquely identified by event_id and is associated with campaign metadata including campaign_name, campaign_id, campaign_activity, and campaign_activity_name, essential for tracing campaign performance. It records detailed email attributes (emailclient, from_email, send_id), URL specifics (url, url_alias, url_id), and technical data (operatingsystem, browser, device) that facilitate analysis of channel effectiveness and platform behavior. Additional columns such as bounce_category, identity_type, persona_identifier, channel, channel_value, and home_country provide further segmentation for targeting and regulatory compliance, while brand_family links responses to specific PMI product lines. The event_date timestamp supports chronological tracking and trend analyses for strategic marketing insights."},

{"table name":"campaign_taxonomy",
"text":"This table captures detailed metadata for PMI’s marketing campaigns, organizing both outbound and inbound communications into a structured taxonomy that supports campaign analysis and strategic alignment. Key identifiers like campaign_key, promotion_id, and local_action_id uniquely track each campaign, while columns such as scope, communication_direction, and campaign_channel define the reach and direction of interactions. It also delineates channels and consumer touchpoints through fields like outbound_channel, inbound_channel, consumer_entry_point, and platform. Additionally, the table maps customer journeys and promotional milestones using journey_name, journey_activity_name, journey_state, and sequence_type, paired with business-critical metrics from business_objective, timing, and frequency. Other columns such as promotion_value, promotion_benefit, and promotion_type, alongside product_type, product_edition, and product_generation, provide insight into the campaign’s offer details and product associations. This comprehensive schema serves to support semantic queries, detailed campaign performance analytics, and complex NL2SQL mapping requirements."},

{"table name":"case",
"text":"This table encapsulates comprehensive customer care cases for PMI, where each record is uniquely identified by case_identifier. It captures critical classification details using fields such as identity_type, case_record_type_description, case_type, and record_type to differentiate case categories and internal tracking. Key columns like subject, subject_description, and subject_code define the customer issue context, while product-oriented fields including product_family, product_generation, extended_brand_family, and brand_family enable linkage to specific PMI devices and consumables. Operational data such as owner_id, device_codentify, consumable_complaint_reason, case_channel, case_source, and correlation_id facilitate cross-functional case routing and resolution. Date and timeline management is achieved through create_date, closing_date, and latest_update_date, with additional identifiers like appointment_id, case_internal_id, order_id, and persona_identifier enhancing integration across systems and supporting detailed analytics within PMI’s customer care ecosystem."},

{"table name":"consent",
"text":"This table captures consent records related to customer interactions for Philip Morris International, detailing regulatory compliance and user permissions. It includes columns such as terms_and_condition_country and consent_country_extracted that specify the applicable legal jurisdictions, while consent_type and consent_type_extracted classify the nature of the consent. The is_consent_granted field indicates whether permission was granted, and last_consent_modified along with doc_date and doc_version track the temporal aspects and document iterations associated with each consent entry. Unique identifiers like consent_identifier, consent_id, and persona_identifier link these records to individual users and/or profiles, with home_country and identity_type providing additional context about the subject's origin and identification method, thereby supporting critical analyses of legal compliance and customer segmentation."},

{"table name":"consolidated_id",
"text":"This table serves as a centralized mapping repository that links various identity attributes across multiple systems for PMI data integration. It stores key elements such as \"identity_type\" to distinguish between different identification methods, \"source_id\" and \"source_id_raw\" to capture both processed and original identifiers from the originating system, and \"consolidated_id\" functioning as the unified primary identifier. The \"persona_identifier\" aids in associating customer behavioral profiles, while \"source_system\" specifies the origin of data entries, and \"home_country\" provides geographical context. This schema is essential for consolidating fragmented identity data for precise customer segmentation and cross-system analysis in PMI operations."},

{"table name":"control_group",
"text":"This table captures detailed records of control group segments for PMI campaigns, where each entry is uniquely identified by the control_group_id. It logs key temporal markers through submitted_time and created_time, likely representing Unix timestamps for tracking event chronology. The home_country and country columns provide geographical context, while the campaign_id links each control group entry to a specific marketing campaign. The persona_identifier supports segmentation and analysis of user archetypes, enabling nuanced assessment of experimental group behaviors and outcomes in PMI's customer and product engagement studies."},

{"table name":"conversion",
"text":"This table records conversion events where individuals transition partially or fully between market segments, capturing key behavioral shifts for PMI analysis. It documents the customer journey with detailed metadata including the original global and specific questions and answers (original_global_question, original_question, original_answer, original_global_answer) that capture initial engagement. The conversion level and identifiers (conversion_level, conversion_identifier, case_identifier, persona_identifier) uniquely distinguish each event, while fields like survey_id and interaction_id link to broader customer interaction data. Additional details such as source, home_country, product_used_inthepast1week, brand_family, and a timestamp (date) provide context for analyzing trends in consumer conversion behavior and the efficacy of product engagement strategies."},

{"table name":"device",
"text":"This table centrally catalogs detailed PMI device information, capturing product specifics for key devices such as IQOS and ILUMA. Each record is uniquely defined by identification fields like serial_number, device_codentify, and identity_godfather_identifier, while additional product codes (device_product_code, variant_product_code, pack_codentify) ensure precise tracking. Core attributes such as device_description, device_type, device_version, device_color, and device_material_group describe the physical and functional characteristics, whereas columns like condition, grade, and brand_differentiator signal quality and market positioning. Warranty periods (start_of_warranty_date, end_of_warranty_date), purchase_date, registration_device_date, and replacement_date facilitate lifecycle analysis, while status fields (status, disabled, proof_of_purchase_status, trade_in_status, is_for_trial) monitor product lifecycle, usage, and trade-in conditions. Supplementary columns including platform, home_country, identity_type, persona_identifier, component_code, and references to device replacements (replaces, replaced_by) further support operational analytics and relational mappings in customer-product interactions."},

{"table name":"device_action",
"text":"This table captures detailed event logs for device interactions within the PMI ecosystem, uniquely tracking each action via identifiers such as \"id\", \"action_id\", and \"correlation_id\". It records the timing of these interactions with \"device_action_created_date\", \"action_date\", and \"modified_date\", supporting chronological analysis of device events. Columns like \"device_codentify\" and \"asset_id\" link specific devices and assets to recorded activities, while \"persona_identifier\" associates actions with individual user profiles. The \"channel\", \"modified_by\", and \"device_action_created_by\" fields provide context on the operational source and administrating agents behind each action, and \"variant_product_code\" offers insight into product-specific variants potentially including devices like IQOS or ILLUMA. The \"home_country\" field further contextualizes the geographical origin of the action, collectively enabling robust tracking and multi-dimensional analysis of device-related behavior."},

{"table name":"identity",
"text":"This table captures comprehensive identity records for PMI’s registered legal age users (LAU) and legal age smokers (LAS), integrating consent details and opt-in preferences for channels and products such as IQOS. It stores key regulatory and marketing indicators including accepted_privacy_policy, accepted_terms_and_conditions, various opt-in flags (iqos_opt_in, veev_opt_in, call_communication_opt_in, phone_comunication_opt_in, email_comunication_opt_in, global_opt_in, soft_marketing_opt_in_flag), and program-specific markers like care_plus, qure, and qoach. Core identifiers such as identity_unique_identifier and registration_id link users to their demographic (first_name, last_name, date_of_birth, gender, preferred_language) and contact data (email_address, phone_number with phone_country_code_number, residence_state, residence_city, residence_zipcode, residence_address), while timestamps (registration_date, identity_creation_date, lastmodified, last_login_date, opt_in_last_updated_date) trace their activity and profile updates. Additional fields like registration_touchpoint_id, registration_campaign_activity_id, and registration_source_app provide context for user acquisition channels and event tracking, ensuring robust verification, compliance, and segmentation for targeted marketing and operational analysis."},

{"table name":"interaction",
"text":"This table captures detailed transactional events reflecting interactions initiated by Coaches, CSC Agents, or Consumers within the PMI ecosystem, serving as both an operational log and a business audit trail. Key identifiers such as interaction_id, case_id, and contract_id link records across systems, while temporal data captured in date_time ensures precise chronological tracking. Core columns like location_description, location_id, and location_address, along with market_refcode, country_refcode, and state_id, provide geographical context for each event. The table also categorizes interactions via fields such as category, interaction_type_refcode, case_type, channel_refcode, and document_type, and integrates financial dimensions with order_amount and currency. Additional identifiers including external_reference, sap_id, friend_id, correlation_id, and campaign_id facilitate cross-referencing and comprehensive analysis of consumer behavior, vendor performance, and multi-channel engagement. This dense, multifaceted dataset supports business process monitoring, regulatory compliance, and actionable insights into customer and account activities."},

{"table name":"interaction_device",
"text":"This table captures detailed device-related information linked to customer interactions within PMI's ecosystem, crucial for analyzing engagement patterns and regulatory compliance. Each record is anchored by a unique interaction identifier (interaction_id) and incorporates the customer's geographic context via home_country, while persona_identifier associates the interaction with specific customer profiles. The date_time column, recorded as a bigint timestamp, marks the exact interaction moment, and device attributes such as device_id and device_version detail the gadget used. The interaction_type_refcode categorizes the nature of the event, collectively enabling sophisticated tracking of connected device usage in tandem with customer behavior for targeted marketing insights."},

{"table name":"interaction_flavour",
"text":"This table captures detailed records of product consumable interactions, linking key flavor attributes to customer engagements within the PMI ecosystem. Each entry is uniquely identified by an interaction via the `interaction_id` and includes flavor metadata such as `flavour_refname` and `flavour_refcode` necessary for mapping consumable variants used across products like IQOS and ILLUMA. The `interaction_type_refcode` distinguishes different types of consumption events, while `persona_identifier` segments records by user profile. Additional context is provided by `home_country`, indicating the geographical origin of the interaction, and `date_time`, a bigint timestamp that enables chronological analysis of consumption patterns and user behavior."},

{"table name":"interaction_product",
"text":"This table records detailed product data linked to customer interactions across PMI channels, with each entry uniquely identified by the interaction_id. It captures the home_country and platform of the interaction and specifies the product using both product_name and product_id. The interaction_type_refcode classifies the nature of engagement, while consolidated_brand_family groups products under PMI portfolios, potentially including key lines like IQOS or ILLUMA. Additional context is provided by the category and persona_identifier fields, with date_time (as a timestamp) offering a chronological perspective, enabling nuanced analysis of product interactions across regions and consumer segments."},

{"table name":"last_activity",
"text":"This table logs the most recent interaction events for PMI-related entities, capturing key details such as the communication medium via last_activity_channel and the nature of the event through last_activity_action. It records the activity timestamp in last_activity_date (as bigint) and computes temporal recency with days_since_last_activity_date, providing crucial metrics for behavior analysis. The last_activity_table field indicates the originating module or dataset, while persona_identifier serves as the unique key linking to broader customer profiles. Additionally, home_country offers geo-demographic context, making the table valuable for tracking engagement patterns, segmentation, and correlating interactions with PMI device adoption like IQOS or ILLUMA."},

{"table name":"loyalty_activity",
"text":"This table logs detailed consumer loyalty transactions within the PMI loyalty ecosystem, recording every event that earns or redeems points. Each record is uniquely identified by identifiers such as transaction_id, activity_identifier, and action_id, while action_date and action_update_date capture the event timestamps. Core columns include statuspoints and redemptionpoints for tracking point balances, with status_point_expire_date and redemption_point_expire_date denoting expiry thresholds. The table further contextualizes each event with id_type, id_value, related_id_type, and related_value, explaining the linkage between transactions and associated consumer or campaign identifiers. Supplementary fields like action_name, reason, and conversion_amount provide insights into the nature and value of the activity, and local specificity is maintained through site_name, site_id, and home_country, ensuring precise geographic attribution for loyalty behavior analysis."},

{"table name":"loyalty_summary",
"text":"This table encapsulates a detailed snapshot of consumer loyalty accounts at PMI, tracking membership milestones and point transactions crucial for transitioning between loyalty tiers—Bronze, Silver, and Gold. Key columns such as persona_identifier and summary_identifier serve as primary keys linking loyalty records to individual consumer profiles. It records essential dates like join_date and next_points_expiration_date along with metrics including total_redeemed_points, ytd_status_points, and redemption_points to monitor point accrual and usage. Additional columns, including current_tier, next_tier, and status_points_required_for_next_tier, support dynamic tier progression analysis, while site_id and site_name contextualize the loyalty scheme site specifics. Fields like conversion_amount and next_redemption_points_expiration_value provide insights for operational and revenue impact evaluations, making the table vital for strategic customer engagement and loyalty performance analytics."},

{"table name":"nba_action",
"text":"This table defines the next best actions (NBA) recommended for consumers at various stages of their journey, integrating promotion details and action classifications critical for PMI's targeted marketing strategies. It includes descriptive fields such as \"description\", \"promotion_benefit\", \"promotion_value\", \"promotion\", and \"promotion_type\" that encapsulate the nature of each action. Key timing and status columns such as \"active\", \"expiration_date\", \"published\", \"last_modified_date_src\", and \"created_date_src\" ensure accurate tracking of promotion validity and updates. The \"channels\" column outlines communication platforms, while \"priority\" assigns importance levels, and \"typology_name\" with \"typology_id\" classify the specific action group. Unique identifiers \"global_action_id\" and \"action_identifier\" support cross-referencing within PMI's broader ecosystem, and additional fields like \"promotion_id\", \"name\", and \"country\" facilitate segmentation and localization of consumer recommendations."},

{"table name":"order",
"text":"This table captures comprehensive details of legally binding customer orders, encapsulating confirmed requests to buy, sell, deliver, or receive products under specified terms. It records key identifiers such as order_identifier, marketplace_order_id, and order_correlation_id, linking transactions to broader customer interactions. The order’s nature and processing are described through columns like order_channel, order_type, order_status, payment_status, and cancellation_reason_code, while financial elements are detailed with fields including item_price, order_amount, and tradein_discounted_amount. It integrates product-specific information through multiple codes (base_product_code, base_pmi_product_code, variant_pmi_product_code, global_product_code, product_code) and descriptive attributes (base_name_en, variant_name_en, item_description, variant_color_name_en), which are critical for tracking PMI’s product variants such as IQOS or ILLUMA. Additional data such as shipping_method, shipping_date, delivery_tracking, and marketplace_name illuminate fulfillment logistics, and ancillary columns like lending_expiration_time, lending_order_status, and lending_extension_flag support extended service or rental models. Other columns additionally provide context with location details (location_name, location_id, home_country, country), payment_method, platform, and persona_identifier, thereby facilitating integrated analytic queries across customer behavior, market segmentation, and operational workflow management in PMI’s commercial ecosystem."},

{"table name":"order_discount",
"text":"This table captures detailed discount data applied at either the order or item level within PMI transactions, highlighting both promotional coupons and consumer-issued vouchers. It integrates comprehensive product variant details—such as variant_pmi_product_code, variant_product_code, base_product_code, base_pmi_product_code, variant_color_name_en, and variant_brand_family_name—to accurately map discounts to specific device models like IQOS or ILLUMA. Essential identifiers including order_identifier, item_identifier, discount_item_no, and persona_identifier enable precise linkage with customer and order records, while financial columns discount_net and discount_gross quantify discount impacts. Additional fields such as voucher_code, discount_description, and discount_type provide context for the discount origin, and geographical segmentation is addressed through home_country, collectively supporting robust revenue reconciliation and targeted marketing analytics."},

{"table name":"persona_segmentation",
"text":"This table encapsulates detailed segmentation data for PMI customer personas, integrating identifiers and descriptive fields to support precise audience targeting and campaign analytics. Each record is uniquely mapped using the persona’s segmentation identifier (persona_identifier) and segment_id, with segmentation defined across multiple dimensions including geography (segment_country and country), temporal validity (segment_date as a bigint and expired_date as a double), and categorical metadata (segment_channel, segment_category, and segment). The source_segment and source_segment_ref_id columns capture the originating segmentation framework, while segment_description and segment_value provide contextual insights and evaluative data. This dense, multi-faceted segmentation schema enables refined analysis of consumer behavior patterns crucial for tailored marketing strategies and compliance within PMI’s operations."},

{"table name":"rating_value",
"text":"This table captures detailed customer rating responses, integrating temporal, geographical, and survey metadata to support analytical queries on product feedback and market interactions. Key columns include numeric timestamps in submission_date and last_publish_time to record event chronology, and answer – a numerical rating that quantifies customer sentiment. The review_id serves as a unique identifier for each feedback instance, while persona_identifier links to customer identity segments, aiding in demographic or behavioral segmentation. Complementary text fields such as rating_country, home_country, question_label, question_type, and question_id provide contextual details on the origin and nature of the questions posed, enabling nuanced analysis of customer experiences and regulatory profiles relevant to PMI’s targeted markets."},

{"table name":"survey",
"text":"This table aggregates survey data sourced from SFMC, Qualtrics, and Bazaar Voice reviews, capturing both questions and corresponding answers to provide a comprehensive view of customer feedback. It features primary identifiers such as survey_response_id, survey_identifier, question_id, and answer_id that link responses and questions across various digital channels. Key metadata columns like source, url, channel_label, and distribution_channel specify the origin and context of each survey entry, while additional fields (e.g., transaction_identifier, communication_id, touchpoint_identifier, and touchpoint_detail) provide granular insights into the touchpoints and interactions. Temporal markers such as start_date and end_date along with demographic indicators like country, home_country, and consumer_program enable nuanced analysis of campaign performance and consumer behavior within the PMI ecosystem."},

{"table name":"survey_callback",
"text":"This table captures post-survey callback interactions and sentiment analysis for PMI customers, uniquely associating each record with a survey via the `survey_id` and linking service cases through `ticket_id`. It logs key follow-up directives in `next_steps`, while documenting user sentiment through `positive_mentions` and `negative_mentions`, and assessing urgency via the `priority` field. Additional fields such as `home_country` and `country` provide geographic context, whereas `persona_identifier` facilitates customer segmentation. Operational flags like `sentiment_management_performed`, `immediate_watchout`, and `callback_performed` indicate the status and effectiveness of post-survey interventions, ensuring a detailed audit trail for customer support and strategic follow-ups."},

You must decide which tables from the above list are needed to create an SQL query, then you will output the table names in a list. you MUST PROVIDE THE TABLE NAMES in this OUTPUT and you should use any table names that seem remotely likey to be used
    
    """),
    #tools=[get_relavant_table],

    output_type=table_list,
)



relevance_agent=Agent(
    name="relevance_agent",
    instructions="The user seems to have asked a question which doesn't seem relevant to my job. I need to remind the user that I can assist them in answering questions regarding table descriptions, SQL statments and other metadata information reagarding the company's database"
)

agent = Agent(
    name="Main router",
    instructions=("An employee of a large FMCG company is asking a question that can be answered using the company's database You need to determine which action should be taken next"
    "if they have a question which first requires to know which tables to use based on the table decriptions, hand off to the table_fetcher agent since you don't know the naming convention of the tables"      
    "if they have a question about the database like which tables store certain data or which tables exist in the database then hand off to metadata_sql agent"
    "If the query is irrelvant to the database then hand off to relevance_agent"        
    ),
    model="o3-mini",
    handoffs=[table_fetcher, metadata_sql, relevance_agent],
    #tools=[get_weather],
)


sql_generator = Agent (
    name="sql Writer",
    instructions="An employee of a large FMCG company is asking a question that can be answered using the company's database, you have been given a information about the relevant tables that should be used to answer this question, you have been given column names as well for each of these tables, your job is to write an accurate SQL query that can be run to answer this question. Use only the table and column information that has been provided to you. Also whenever you filter or search on a country, use the 2 letter couuntry code like PK or DE. Also when you filter on time make sure to use the UNIX timestamp format (example: '1738669909') however the UNIX time columns are stored as VARCHAR so make the necessary conversions. REMEMBER THAT THIS IS FOR MySQL database so the synatx must conform to it. MAKE SURE TO LIMIT THE RESULT SET to 20 as we have to display this in a browswer. Give a brief explnation of why your thought process of coming up with this query.",
    model="o3-mini",
    output_type=sql_generation_format 

)


sql_executor = Agent(
    name="SQL executor",
    instructions="You have been given an SQL query by the user, your job is to execute the SQL query, use the tool 'run_sql' to cleanly execute the query and return the results" ,
    tools=[run_sql],

    
)

sql_result_analyser= Agent (
    name="SQL result analyser",
    #instructions="The user asked a question and our agent wrote an sql query to answer the question. We have run the SQL query and got it results, your job is to assess the results and decide wether this sql query was good engouh to answer the question or do we need to go back to the drawing board to re-write the query. Return True if the result set answers the user's question, return False if it's need to re-write it. And also give a brief explanation about your choice",
    instructions="The user asked a question and our agent wrote an sql query to answer the question. We have run the SQL query and got it results, your job is to analyse the results and give a brief explanation about the result, you shouldn't echo back the results that you are analysing as the user can also see the raw data, instead provide some insights. PLease note that this data belongs to Phillip Morris consumer segmentaton team",
    #output_type=sql_output_quality_checker
)



async def main():
    if user_text:
        st.info(f"### Q: {user_text}")
        st.divider()
        #result = await Runner.run(agent, "how many rows does the campaign_activity table have?")
        #input_2=result.to_input_list()
        #print(result.final_output)
        
        #print("RESULY FOR input2= "+str(input_2))
        ###result_2 = await Runner.run(SQL_creator,input_2)
        ###print(result_2.final_output)

        #input_prompt = input("how can I help you?")
        with trace("Deterministic workflow"):
            #query="how many uniqe campains have we run?"
            #query="Which channels were most frequently used for campaign contact"
            #query="Which channels were most frequently used for campaign response"
            #query="Which devices were most common for campaign responses"
            #query="List the top URLs clicked"
            query = "Why did so many users move from Hesitaters to Dormant last month"
            
            query = user_text
            
            with st.spinner("Searching for relevant tables..."):
                table_search_result= await Runner.run(
                table_fetcher,
                #input_prompt,
                query
                )

            tables = table_search_result.final_output
            print(table_search_result.final_output)
            #st.write(table_search_result.final_output)
            filtered = [table for table in db_dict if table["table name"] in tables.tables]
            
            st.markdown("### Tables Selected:")
            df = pd.DataFrame(filtered)
            st.dataframe(
                df.style.set_properties(**{
                    'border-color': 'black',
                    'font-weight': 'bold'
                }),
                use_container_width=True
            )
            
            #if filtered:
            #    st.dataframe(pd.DataFrame(filtered), use_container_width=True)
                # Optional: also show as bullets
            #else:
            #    st.info("No matches found for the provided table names.")
                        
            print("\n\n\n "+ str(filtered))

            st.divider()
            with st.spinner("Generating SQL Query to help answer question..."):
                second_query=f"""User's question: {query} 
                table and column information provided: {filtered}
                """
                sql_query_result= await Runner.run(
                sql_generator, 
                second_query
                )
                print("\n\n\n")
                print(second_query)
                sql_generation_result= sql_query_result.final_output
                print(sql_generation_result)
            st.markdown("### SQL Generated:")
            st.code(f" {sql_generation_result.sql_query}")
            st.success(f"##### Explanation: {sql_generation_result.explanation}")
            
            st.divider()
            
            with st.spinner("Executing Query on Database..."):   
                third_query=f""" 
                the SQL query is mentioned here, please execute it and return the result: 
                {sql_query_result.final_output}
                """
                query_execution_result= await Runner.run(
                sql_executor,
                third_query    
                )
                print("CHECKSS !@#")
                print(query_execution_result.final_output)
                print("CHECKSS !@# 22222")
            if df_result_set is not None:
                st.markdown("### Query Result:")
                st.table(df_result_set.reset_index(drop=True))               
            
            st.divider()
            with st.spinner("Analysing Results..."):
                fourth_query=f""" 
                the user's inital question was: {query},
                
                the tables we chose to answer this question were: {tables}
                
                here is some information about the tables: {filtered}
                
                This is the query that we wrote:{sql_query_result.final_output}
                
                this is the result that we got when we ran the query: {query_execution_result.final_output}
                """

                analyser_result= await Runner.run(
                sql_result_analyser,
                fourth_query 
                )
            print(analyser_result.final_output)
            st.markdown("### Result Analysis:")
            st.success(analyser_result.final_output)




if __name__ == "__main__":
    asyncio.run(main())    