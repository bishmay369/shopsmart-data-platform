# architecture_diagram.py
import os
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.analytics import (
    DataFactories, Databricks, SynapseAnalytics, 
    EventHubs, StreamAnalyticsJobs
)

# FIXED: DataLakeStorage for Gen2 architecture
from diagrams.azure.storage import DataLakeStorage, BlobStorage, StorageAccounts

# FIXED: Removed the unused/broken Azure PostgreSQL import!
from diagrams.azure.database import SQLDatabases, CosmosDb

from diagrams.azure.ml import MachineLearningServiceWorkspaces
from diagrams.azure.security import KeyVaults
from diagrams.azure.devops import Repos, Pipelines
from diagrams.azure.monitor import Monitor
from diagrams.azure.web import AppServices
from diagrams.azure.general import Resourcegroups
from diagrams.onprem.database import PostgreSQL, MongoDB
from diagrams.onprem.analytics import PowerBI
from diagrams.programming.framework import FastAPI
from diagrams.onprem.mlops import Mlflow
from diagrams.generic.storage import Storage
from diagrams.custom import Custom

# ============================================
# MAIN ARCHITECTURE DIAGRAM
# ============================================
with Diagram(
    "ShopSmart AI - Intelligent Data Platform",
    show=True,
    direction="TB",  # Top to Bottom
    filename="architecture_main",
    outformat="png",
    graph_attr={
        "fontsize": "28",
        "bgcolor": "white",
        "pad": "0.5",
        "dpi": "200"
    }
):
    
    # ============================================
    # LAYER 1: DATA SOURCES
    # ============================================
    with Cluster("Data Sources", graph_attr={"bgcolor": "#E8F5E9", "style": "rounded"}):
        postgres = PostgreSQL("Orders DB\n(PostgreSQL)")
        mongodb = MongoDB("Clickstream\n(MongoDB)")
        api = FastAPI("Product API\n(REST)")
        csv_files = Storage("Inventory\n(CSV/JSON)")
        iot = Storage("Store Sensors\n(IoT)")
    
    # ============================================
    # LAYER 2: INGESTION
    # ============================================
    with Cluster("Ingestion Layer", graph_attr={"bgcolor": "#E3F2FD", "style": "rounded"}):
        with Cluster("Batch Ingestion"):
            adf = DataFactories("Azure Data\nFactory")
        
        with Cluster("Stream Ingestion"):
            eventhub = EventHubs("Azure\nEvent Hubs")
        
        with Cluster("API Ingestion"):
            functions = AppServices("Azure\nFunctions")
    
    # ============================================
    # LAYER 3: STORAGE - DATA LAKE
    # ============================================
    with Cluster("Azure Data Lake Gen2 (Medallion Architecture)", 
                 graph_attr={"bgcolor": "#FFF3E0", "style": "rounded"}):
        
        with Cluster("🥉 Bronze Layer\n(Raw Data)"):
            bronze = DataLakeStorage("Raw Parquet\nJSON Files")
        
        with Cluster("🥈 Silver Layer\n(Cleaned & Validated)"):
            silver = DataLakeStorage("Delta Tables\n(Cleaned)")
        
        with Cluster("🥇 Gold Layer\n(Business Ready)"):
            gold = DataLakeStorage("Star Schema\n(Delta Tables)")
        
        with Cluster("🗑️ Quarantine"):
            quarantine = DataLakeStorage("Bad Records")
    
    # ============================================
    # LAYER 4: PROCESSING
    # ============================================
    with Cluster("Processing Layer", graph_attr={"bgcolor": "#F3E5F5", "style": "rounded"}):
        with Cluster("Batch Processing"):
            databricks = Databricks("Azure\nDatabricks")
        
        with Cluster("Stream Processing"):
            stream_analytics = StreamAnalyticsJobs("Spark Structured\nStreaming")
        
        with Cluster("Data Quality"):
            # Check if custom icon exists, else fallback to Databricks icon
            icon_path = "./icons/great_expectations.png"
            if os.path.exists(icon_path):
                dq = Custom("Great\nExpectations", icon_path)
            else:
                dq = Databricks("Data Quality\nFramework")
    
    # ============================================
    # LAYER 5: AI/ML
    # ============================================
    with Cluster("AI/ML Layer", graph_attr={"bgcolor": "#FCE4EC", "style": "rounded"}):
        mlflow_svc = Mlflow("MLflow\nExperiment Tracking")
        
        with Cluster("ML Models"):
            segmentation = MachineLearningServiceWorkspaces("Customer\nSegmentation\n(K-Means)")
            forecast = MachineLearningServiceWorkspaces("Demand\nForecasting\n(Prophet)")
            anomaly = MachineLearningServiceWorkspaces("Anomaly\nDetection\n(Isolation Forest)")
    
    # ============================================
    # LAYER 6: SERVING
    # ============================================
    with Cluster("Serving Layer", graph_attr={"bgcolor": "#E0F2F1", "style": "rounded"}):
        synapse_sql = SynapseAnalytics("Synapse\nServerless SQL")
        azure_sql = SQLDatabases("Azure SQL DB\n(Aggregated)")
        cosmos = CosmosDb("Cosmos DB\n(Real-time)")
    
    # ============================================
    # LAYER 7: VISUALIZATION
    # ============================================
    with Cluster("Visualization & Consumption", graph_attr={"bgcolor": "#FFFDE7", "style": "rounded"}):
        powerbi = PowerBI("Power BI\nDashboards")
        streamlit = AppServices("Streamlit\nML App")
        rest_api = FastAPI("REST API\n(FastAPI)")
    
    # ============================================
    # LAYER 8: GOVERNANCE
    # ============================================
    with Cluster("Governance & Security", graph_attr={"bgcolor": "#EFEBE9", "style": "rounded"}):
        keyvault = KeyVaults("Azure\nKey Vault")
        purview = Resourcegroups("Microsoft\nPurview")
        monitor = Monitor("Azure\nMonitor")
    
    # ============================================
    # LAYER 9: DEVOPS
    # ============================================
    with Cluster("DevOps & Orchestration", graph_attr={"bgcolor": "#F5F5F5", "style": "rounded"}):
        github = Repos("GitHub\nActions CI/CD")
        terraform = Pipelines("Terraform\nIaC")
        adf_orch = DataFactories("ADF\nOrchestration")
    
    # ============================================
    # CONNECTIONS (Data Flow)
    # ============================================
    
    # Sources → Ingestion
    postgres >> Edge(color="green", label="CDC/Batch") >> adf
    mongodb >> Edge(color="green", label="Change Stream") >> eventhub
    api >> Edge(color="green", label="REST Pull") >> functions
    csv_files >> Edge(color="green", label="File Drop") >> adf
    iot >> Edge(color="green", label="Events") >> eventhub
    
    # Ingestion → Bronze
    adf >> Edge(color="blue", label="Raw Load") >> bronze
    eventhub >> Edge(color="blue", label="Stream") >> bronze
    functions >> Edge(color="blue", label="API Data") >> bronze
    
    # Bronze → Silver (Processing)
    bronze >> Edge(color="orange", label="Clean & Validate") >> databricks
    databricks >> Edge(color="orange") >> silver
    databricks >> Edge(color="red", style="dashed", label="Bad Records") >> quarantine
    
    # Silver → Gold
    silver >> Edge(color="purple", label="Transform & Model") >> databricks
    databricks >> Edge(color="purple") >> gold
    
    # Streaming Path
    bronze >> Edge(color="cyan", label="Stream") >> stream_analytics
    stream_analytics >> Edge(color="cyan") >> silver
    
    # Data Quality
    databricks >> Edge(color="gray", style="dashed") >> dq
    
    # Gold → ML
    gold >> Edge(color="red", label="Features") >> segmentation
    gold >> Edge(color="red") >> forecast
    gold >> Edge(color="red") >> anomaly
    segmentation >> mlflow_svc
    forecast >> mlflow_svc
    anomaly >> mlflow_svc
    
    # Gold → Serving
    gold >> Edge(color="darkblue") >> synapse_sql
    gold >> Edge(color="darkblue") >> azure_sql
    stream_analytics >> Edge(color="darkblue", label="Real-time") >> cosmos
    
    # Serving → Visualization
    synapse_sql >> Edge(color="black") >> powerbi
    azure_sql >> Edge(color="black") >> streamlit
    cosmos >> Edge(color="black") >> rest_api
    mlflow_svc >> Edge(color="black", style="dashed") >> streamlit
    
    # Governance connections
    keyvault >> Edge(color="gray", style="dotted") >> databricks
    purview >> Edge(color="gray", style="dotted") >> gold
    monitor >> Edge(color="gray", style="dotted") >> adf_orch
    
    # DevOps connections
    github >> Edge(color="gray", style="dotted") >> databricks
    terraform >> Edge(color="gray", style="dotted") >> keyvault
    adf_orch >> Edge(color="darkgreen", style="bold") >> adf

print("✅ Architecture diagram generated: architecture_main.png")