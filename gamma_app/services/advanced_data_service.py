"""
Advanced Data Service with Data Processing, ETL, and Analytics
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Iterator
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import aiofiles
import aiohttp
from pathlib import Path
import hashlib
import csv
import xml.etree.ElementTree as ET

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class DataSourceType(Enum):
    """Data source types"""
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    EXCEL = "excel"
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"

class DataFormat(Enum):
    """Data formats"""
    STRUCTURED = "structured"
    SEMI_STRUCTURED = "semi_structured"
    UNSTRUCTURED = "unstructured"
    TIME_SERIES = "time_series"
    GEOSPATIAL = "geospatial"

class ProcessingStatus(Enum):
    """Processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class DataSource:
    """Data source configuration"""
    id: str
    name: str
    source_type: DataSourceType
    connection_string: str
    schema: Optional[Dict[str, Any]] = None
    authentication: Optional[Dict[str, Any]] = None
    headers: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataPipeline:
    """Data pipeline configuration"""
    id: str
    name: str
    description: str
    source_id: str
    destination_id: str
    transformations: List[Dict[str, Any]] = field(default_factory=list)
    schedule: Optional[str] = None
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataProcessingJob:
    """Data processing job"""
    id: str
    pipeline_id: str
    status: ProcessingStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    records_processed: int = 0
    records_total: int = 0
    error_message: Optional[str] = None
    result_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataQualityReport:
    """Data quality report"""
    id: str
    dataset_id: str
    total_records: int
    valid_records: int
    invalid_records: int
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    uniqueness_score: float
    quality_issues: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

class AdvancedDataService:
    """Advanced Data Service with Data Processing, ETL, and Analytics"""
    
    def __init__(self):
        self.data_sources = {}
        self.data_pipelines = {}
        self.processing_jobs = {}
        self.quality_reports = {}
        self.data_cache = {}
        self.processing_queue = asyncio.Queue()
        self.etl_queue = asyncio.Queue()
        
        # Initialize data processors
        self._initialize_processors()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Advanced Data Service initialized")
    
    def _initialize_processors(self):
        """Initialize data processors"""
        try:
            self.processors = {
                'csv': self._process_csv,
                'json': self._process_json,
                'xml': self._process_xml,
                'excel': self._process_excel,
                'database': self._process_database,
                'api': self._process_api,
                'file': self._process_file
            }
            
            self.transformations = {
                'filter': self._transform_filter,
                'map': self._transform_map,
                'aggregate': self._transform_aggregate,
                'join': self._transform_join,
                'pivot': self._transform_pivot,
                'normalize': self._transform_normalize,
                'validate': self._transform_validate,
                'clean': self._transform_clean,
                'enrich': self._transform_enrich,
                'deduplicate': self._transform_deduplicate
            }
            
            logger.info("Data processors initialized")
            
        except Exception as e:
            logger.error(f"Error initializing processors: {e}")
    
    def _start_background_tasks(self):
        """Start background tasks"""
        try:
            # Start processing processor
            asyncio.create_task(self._process_data_jobs())
            
            # Start ETL processor
            asyncio.create_task(self._process_etl_jobs())
            
            logger.info("Background tasks started")
            
        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")
    
    async def _process_data_jobs(self):
        """Process data processing jobs"""
        try:
            while True:
                try:
                    job = await asyncio.wait_for(self.processing_queue.get(), timeout=1.0)
                    await self._execute_processing_job(job)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing data job: {e}")
                    
        except Exception as e:
            logger.error(f"Error in data processing processor: {e}")
    
    async def _process_etl_jobs(self):
        """Process ETL jobs"""
        try:
            while True:
                try:
                    etl_job = await asyncio.wait_for(self.etl_queue.get(), timeout=1.0)
                    await self._execute_etl_job(etl_job)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing ETL job: {e}")
                    
        except Exception as e:
            logger.error(f"Error in ETL processor: {e}")
    
    async def create_data_source(self, data_source: DataSource) -> str:
        """Create data source"""
        try:
            source_id = str(uuid.uuid4())
            data_source.id = source_id
            data_source.created_at = datetime.utcnow()
            data_source.updated_at = datetime.utcnow()
            
            # Test connection
            await self._test_data_source_connection(data_source)
            
            self.data_sources[source_id] = data_source
            
            logger.info(f"Data source created: {source_id}")
            
            return source_id
            
        except Exception as e:
            logger.error(f"Error creating data source: {e}")
            raise
    
    async def _test_data_source_connection(self, data_source: DataSource):
        """Test data source connection"""
        try:
            if data_source.source_type == DataSourceType.DATABASE:
                engine = create_engine(data_source.connection_string)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
            
            elif data_source.source_type == DataSourceType.API:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        data_source.connection_string,
                        headers=data_source.headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status >= 400:
                            raise Exception(f"API connection failed: {response.status}")
            
            elif data_source.source_type == DataSourceType.CSV:
                if not Path(data_source.connection_string).exists():
                    raise Exception("CSV file not found")
            
            logger.info(f"Data source connection tested: {data_source.id}")
            
        except Exception as e:
            logger.error(f"Error testing data source connection: {e}")
            raise
    
    async def create_data_pipeline(self, pipeline: DataPipeline) -> str:
        """Create data pipeline"""
        try:
            pipeline_id = str(uuid.uuid4())
            pipeline.id = pipeline_id
            pipeline.created_at = datetime.utcnow()
            pipeline.updated_at = datetime.utcnow()
            
            # Validate pipeline
            await self._validate_pipeline(pipeline)
            
            self.data_pipelines[pipeline_id] = pipeline
            
            logger.info(f"Data pipeline created: {pipeline_id}")
            
            return pipeline_id
            
        except Exception as e:
            logger.error(f"Error creating data pipeline: {e}")
            raise
    
    async def _validate_pipeline(self, pipeline: DataPipeline):
        """Validate data pipeline"""
        try:
            # Check if source exists
            if pipeline.source_id not in self.data_sources:
                raise ValueError(f"Data source not found: {pipeline.source_id}")
            
            # Check if destination exists
            if pipeline.destination_id not in self.data_sources:
                raise ValueError(f"Data destination not found: {pipeline.destination_id}")
            
            # Validate transformations
            for transformation in pipeline.transformations:
                transform_type = transformation.get('type')
                if transform_type not in self.transformations:
                    raise ValueError(f"Unknown transformation type: {transform_type}")
            
            logger.info("Pipeline validation passed")
            
        except Exception as e:
            logger.error(f"Error validating pipeline: {e}")
            raise
    
    async def execute_pipeline(self, pipeline_id: str) -> str:
        """Execute data pipeline"""
        try:
            if pipeline_id not in self.data_pipelines:
                raise ValueError(f"Pipeline not found: {pipeline_id}")
            
            pipeline = self.data_pipelines[pipeline_id]
            
            # Create processing job
            job_id = str(uuid.uuid4())
            processing_job = DataProcessingJob(
                id=job_id,
                pipeline_id=pipeline_id,
                status=ProcessingStatus.PENDING
            )
            
            self.processing_jobs[job_id] = processing_job
            
            # Add to processing queue
            await self.processing_queue.put(processing_job)
            
            logger.info(f"Pipeline execution started: {job_id}")
            
            return job_id
            
        except Exception as e:
            logger.error(f"Error executing pipeline: {e}")
            raise
    
    async def _execute_processing_job(self, job: DataProcessingJob):
        """Execute data processing job"""
        try:
            job.status = ProcessingStatus.PROCESSING
            job.started_at = datetime.utcnow()
            
            pipeline = self.data_pipelines[job.pipeline_id]
            source = self.data_sources[pipeline.source_id]
            destination = self.data_sources[pipeline.destination_id]
            
            # Extract data
            data = await self._extract_data(source)
            job.records_total = len(data) if hasattr(data, '__len__') else 0
            
            # Transform data
            transformed_data = data
            for transformation in pipeline.transformations:
                transformed_data = await self._apply_transformation(transformed_data, transformation)
                job.records_processed = len(transformed_data) if hasattr(transformed_data, '__len__') else 0
                job.progress = (job.records_processed / job.records_total * 100) if job.records_total > 0 else 100
            
            # Load data
            result_path = await self._load_data(transformed_data, destination)
            job.result_path = result_path
            
            # Update job status
            job.status = ProcessingStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.progress = 100.0
            
            logger.info(f"Processing job completed: {job.id}")
            
        except Exception as e:
            logger.error(f"Error executing processing job: {e}")
            job.status = ProcessingStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
    
    async def _extract_data(self, source: DataSource) -> Any:
        """Extract data from source"""
        try:
            processor = self.processors.get(source.source_type.value)
            if not processor:
                raise ValueError(f"No processor for source type: {source.source_type}")
            
            data = await processor(source)
            
            logger.info(f"Data extracted from source: {source.id}")
            
            return data
            
        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            raise
    
    async def _process_csv(self, source: DataSource) -> pd.DataFrame:
        """Process CSV data source"""
        try:
            df = pd.read_csv(source.connection_string)
            return df
            
        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
            raise
    
    async def _process_json(self, source: DataSource) -> List[Dict[str, Any]]:
        """Process JSON data source"""
        try:
            async with aiofiles.open(source.connection_string, 'r') as f:
                content = await f.read()
                data = json.loads(content)
                return data if isinstance(data, list) else [data]
            
        except Exception as e:
            logger.error(f"Error processing JSON: {e}")
            raise
    
    async def _process_xml(self, source: DataSource) -> List[Dict[str, Any]]:
        """Process XML data source"""
        try:
            tree = ET.parse(source.connection_string)
            root = tree.getroot()
            
            data = []
            for element in root:
                item = {}
                for child in element:
                    item[child.tag] = child.text
                data.append(item)
            
            return data
            
        except Exception as e:
            logger.error(f"Error processing XML: {e}")
            raise
    
    async def _process_excel(self, source: DataSource) -> pd.DataFrame:
        """Process Excel data source"""
        try:
            df = pd.read_excel(source.connection_string)
            return df
            
        except Exception as e:
            logger.error(f"Error processing Excel: {e}")
            raise
    
    async def _process_database(self, source: DataSource) -> pd.DataFrame:
        """Process database data source"""
        try:
            engine = create_engine(source.connection_string)
            query = source.parameters.get('query', 'SELECT * FROM table_name')
            
            df = pd.read_sql(query, engine)
            return df
            
        except Exception as e:
            logger.error(f"Error processing database: {e}")
            raise
    
    async def _process_api(self, source: DataSource) -> List[Dict[str, Any]]:
        """Process API data source"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    source.connection_string,
                    headers=source.headers,
                    params=source.parameters
                ) as response:
                    data = await response.json()
                    return data if isinstance(data, list) else [data]
            
        except Exception as e:
            logger.error(f"Error processing API: {e}")
            raise
    
    async def _process_file(self, source: DataSource) -> str:
        """Process file data source"""
        try:
            async with aiofiles.open(source.connection_string, 'r') as f:
                content = await f.read()
                return content
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            raise
    
    async def _apply_transformation(self, data: Any, transformation: Dict[str, Any]) -> Any:
        """Apply data transformation"""
        try:
            transform_type = transformation.get('type')
            transform_func = self.transformations.get(transform_type)
            
            if not transform_func:
                raise ValueError(f"Unknown transformation: {transform_type}")
            
            transformed_data = await transform_func(data, transformation)
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Error applying transformation: {e}")
            raise
    
    async def _transform_filter(self, data: Any, transformation: Dict[str, Any]) -> Any:
        """Filter data transformation"""
        try:
            if isinstance(data, pd.DataFrame):
                condition = transformation.get('condition')
                if condition:
                    return data.query(condition)
                return data
            
            elif isinstance(data, list):
                filter_func = transformation.get('filter_function')
                if filter_func:
                    return [item for item in data if filter_func(item)]
                return data
            
            return data
            
        except Exception as e:
            logger.error(f"Error in filter transformation: {e}")
            raise
    
    async def _transform_map(self, data: Any, transformation: Dict[str, Any]) -> Any:
        """Map data transformation"""
        try:
            if isinstance(data, pd.DataFrame):
                mapping = transformation.get('mapping', {})
                return data.rename(columns=mapping)
            
            elif isinstance(data, list):
                map_func = transformation.get('map_function')
                if map_func:
                    return [map_func(item) for item in data]
                return data
            
            return data
            
        except Exception as e:
            logger.error(f"Error in map transformation: {e}")
            raise
    
    async def _transform_aggregate(self, data: Any, transformation: Dict[str, Any]) -> Any:
        """Aggregate data transformation"""
        try:
            if isinstance(data, pd.DataFrame):
                group_by = transformation.get('group_by', [])
                aggregations = transformation.get('aggregations', {})
                
                if group_by and aggregations:
                    return data.groupby(group_by).agg(aggregations).reset_index()
                return data
            
            return data
            
        except Exception as e:
            logger.error(f"Error in aggregate transformation: {e}")
            raise
    
    async def _transform_join(self, data: Any, transformation: Dict[str, Any]) -> Any:
        """Join data transformation"""
        try:
            if isinstance(data, pd.DataFrame):
                # This would require a second dataset
                # For now, return the original data
                return data
            
            return data
            
        except Exception as e:
            logger.error(f"Error in join transformation: {e}")
            raise
    
    async def _transform_pivot(self, data: Any, transformation: Dict[str, Any]) -> Any:
        """Pivot data transformation"""
        try:
            if isinstance(data, pd.DataFrame):
                index = transformation.get('index')
                columns = transformation.get('columns')
                values = transformation.get('values')
                
                if index and columns and values:
                    return data.pivot_table(index=index, columns=columns, values=values)
                return data
            
            return data
            
        except Exception as e:
            logger.error(f"Error in pivot transformation: {e}")
            raise
    
    async def _transform_normalize(self, data: Any, transformation: Dict[str, Any]) -> Any:
        """Normalize data transformation"""
        try:
            if isinstance(data, pd.DataFrame):
                columns = transformation.get('columns', [])
                method = transformation.get('method', 'minmax')
                
                for column in columns:
                    if column in data.columns:
                        if method == 'minmax':
                            data[column] = (data[column] - data[column].min()) / (data[column].max() - data[column].min())
                        elif method == 'zscore':
                            data[column] = (data[column] - data[column].mean()) / data[column].std()
                
                return data
            
            return data
            
        except Exception as e:
            logger.error(f"Error in normalize transformation: {e}")
            raise
    
    async def _transform_validate(self, data: Any, transformation: Dict[str, Any]) -> Any:
        """Validate data transformation"""
        try:
            if isinstance(data, pd.DataFrame):
                rules = transformation.get('rules', [])
                
                for rule in rules:
                    column = rule.get('column')
                    rule_type = rule.get('type')
                    value = rule.get('value')
                    
                    if column in data.columns:
                        if rule_type == 'not_null':
                            data = data[data[column].notna()]
                        elif rule_type == 'greater_than':
                            data = data[data[column] > value]
                        elif rule_type == 'less_than':
                            data = data[data[column] < value]
                        elif rule_type == 'equals':
                            data = data[data[column] == value]
                
                return data
            
            return data
            
        except Exception as e:
            logger.error(f"Error in validate transformation: {e}")
            raise
    
    async def _transform_clean(self, data: Any, transformation: Dict[str, Any]) -> Any:
        """Clean data transformation"""
        try:
            if isinstance(data, pd.DataFrame):
                # Remove duplicates
                if transformation.get('remove_duplicates', False):
                    data = data.drop_duplicates()
                
                # Handle missing values
                missing_strategy = transformation.get('missing_strategy')
                if missing_strategy == 'drop':
                    data = data.dropna()
                elif missing_strategy == 'fill':
                    fill_value = transformation.get('fill_value', 0)
                    data = data.fillna(fill_value)
                
                return data
            
            return data
            
        except Exception as e:
            logger.error(f"Error in clean transformation: {e}")
            raise
    
    async def _transform_enrich(self, data: Any, transformation: Dict[str, Any]) -> Any:
        """Enrich data transformation"""
        try:
            if isinstance(data, pd.DataFrame):
                # Add calculated columns
                calculations = transformation.get('calculations', [])
                
                for calc in calculations:
                    column_name = calc.get('column')
                    expression = calc.get('expression')
                    
                    if column_name and expression:
                        data[column_name] = data.eval(expression)
                
                return data
            
            return data
            
        except Exception as e:
            logger.error(f"Error in enrich transformation: {e}")
            raise
    
    async def _transform_deduplicate(self, data: Any, transformation: Dict[str, Any]) -> Any:
        """Deduplicate data transformation"""
        try:
            if isinstance(data, pd.DataFrame):
                subset = transformation.get('subset')
                keep = transformation.get('keep', 'first')
                
                if subset:
                    data = data.drop_duplicates(subset=subset, keep=keep)
                else:
                    data = data.drop_duplicates(keep=keep)
                
                return data
            
            return data
            
        except Exception as e:
            logger.error(f"Error in deduplicate transformation: {e}")
            raise
    
    async def _load_data(self, data: Any, destination: DataSource) -> str:
        """Load data to destination"""
        try:
            # Create output directory
            output_dir = Path("gamma_app/data/output")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate output filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"processed_data_{timestamp}.csv"
            
            # Save data based on type
            if isinstance(data, pd.DataFrame):
                data.to_csv(output_file, index=False)
            elif isinstance(data, list):
                if data and isinstance(data[0], dict):
                    df = pd.DataFrame(data)
                    df.to_csv(output_file, index=False)
                else:
                    async with aiofiles.open(output_file, 'w') as f:
                        await f.write('\n'.join(str(item) for item in data))
            else:
                async with aiofiles.open(output_file, 'w') as f:
                    await f.write(str(data))
            
            logger.info(f"Data loaded to: {output_file}")
            
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    async def analyze_data_quality(self, dataset_id: str) -> str:
        """Analyze data quality"""
        try:
            # Create quality report
            report_id = str(uuid.uuid4())
            
            # This would analyze the actual dataset
            # For now, create a mock report
            quality_report = DataQualityReport(
                id=report_id,
                dataset_id=dataset_id,
                total_records=1000,
                valid_records=950,
                invalid_records=50,
                completeness_score=0.95,
                accuracy_score=0.92,
                consistency_score=0.88,
                uniqueness_score=0.96,
                quality_issues=[
                    {'type': 'missing_values', 'column': 'email', 'count': 25},
                    {'type': 'duplicates', 'column': 'id', 'count': 15},
                    {'type': 'invalid_format', 'column': 'phone', 'count': 10}
                ]
            )
            
            self.quality_reports[report_id] = quality_report
            
            logger.info(f"Data quality report created: {report_id}")
            
            return report_id
            
        except Exception as e:
            logger.error(f"Error analyzing data quality: {e}")
            raise
    
    async def get_processing_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get processing job status"""
        try:
            if job_id not in self.processing_jobs:
                return None
            
            job = self.processing_jobs[job_id]
            
            return {
                'id': job.id,
                'pipeline_id': job.pipeline_id,
                'status': job.status.value,
                'progress': job.progress,
                'records_processed': job.records_processed,
                'records_total': job.records_total,
                'created_at': job.created_at.isoformat(),
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'error_message': job.error_message,
                'result_path': job.result_path
            }
            
        except Exception as e:
            logger.error(f"Error getting processing status: {e}")
            return None
    
    async def get_quality_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get data quality report"""
        try:
            if report_id not in self.quality_reports:
                return None
            
            report = self.quality_reports[report_id]
            
            return {
                'id': report.id,
                'dataset_id': report.dataset_id,
                'total_records': report.total_records,
                'valid_records': report.valid_records,
                'invalid_records': report.invalid_records,
                'completeness_score': report.completeness_score,
                'accuracy_score': report.accuracy_score,
                'consistency_score': report.consistency_score,
                'uniqueness_score': report.uniqueness_score,
                'quality_issues': report.quality_issues,
                'created_at': report.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting quality report: {e}")
            return None
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            status = {
                'service': 'Advanced Data Service',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'data_sources': {
                    'total': len(self.data_sources),
                    'by_type': {}
                },
                'pipelines': {
                    'total': len(self.data_pipelines),
                    'enabled': len([p for p in self.data_pipelines.values() if p.enabled])
                },
                'jobs': {
                    'total': len(self.processing_jobs),
                    'completed': len([j for j in self.processing_jobs.values() if j.status == ProcessingStatus.COMPLETED]),
                    'failed': len([j for j in self.processing_jobs.values() if j.status == ProcessingStatus.FAILED]),
                    'running': len([j for j in self.processing_jobs.values() if j.status == ProcessingStatus.PROCESSING])
                },
                'quality_reports': {
                    'total': len(self.quality_reports)
                },
                'queues': {
                    'processing_queue_size': self.processing_queue.qsize(),
                    'etl_queue_size': self.etl_queue.qsize()
                },
                'processors': {
                    'data_processors': len(self.processors),
                    'transformations': len(self.transformations)
                }
            }
            
            # Count data sources by type
            for source in self.data_sources.values():
                source_type = source.source_type.value
                status['data_sources']['by_type'][source_type] = status['data_sources']['by_type'].get(source_type, 0) + 1
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'service': 'Advanced Data Service',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


























