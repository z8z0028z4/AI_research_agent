"""
核心模組
======

提供系統的核心功能，包括：
- Schema 管理
- 向量庫管理
- LLM 管理
- 模式管理
- 處理器模組
"""

from .schema_manager import (
    get_dynamic_schema_params,
    create_research_proposal_schema,
    create_experimental_detail_schema,

    create_revision_proposal_schema,
    get_schema_by_type
)

from .vector_store import (
    load_paper_vectorstore,
    load_experiment_vectorstore,
    search_documents,
    get_vectorstore_stats,
    preview_chunks,
    combine_search_results,
    format_search_results
)

from .retrieval import (
    retrieve_chunks_multi_query,
    retrieve_chunks_single_query
)

from .query_expander import (
    expand_query,
    expand_query_with_fallback
)

from .generation import (
    call_llm,
    call_llm_structured_proposal,
    call_llm_structured_experimental_detail,

    call_llm_structured_revision_proposal
)

from .format_converter import (
    structured_proposal_to_text,
    structured_experimental_detail_to_text,
    structured_revision_proposal_to_text
)

from .llm_manager import (
    LLMManager,
    create_llm_manager,
    get_default_llm_manager
)

from .mode_manager import (
    get_available_modes,
    validate_mode,
    get_mode_description,
    get_mode_config,
    get_modes_by_category,
    is_structured_output_mode,
    requires_experiment_data,
    allows_inference,
    get_mode_summary
)

from .processors import (
    BaseProcessor,
    AdvancedInferenceProcessor,
    ProposalProcessor,
    InferenceProcessor,
    StrictProcessor,
    ExperimentDetailProcessor,
    InnovationProcessor,
    get_processor
)

from .prompt_builder import (
    build_prompt,
    build_inference_prompt,
    build_proposal_prompt,
    build_detail_experimental_plan_prompt,
    build_dual_inference_prompt,
    build_iterative_proposal_prompt
)

__all__ = [
    # Schema 管理
    "get_dynamic_schema_params",
    "create_research_proposal_schema",
    "create_experimental_detail_schema",

    "create_revision_proposal_schema",
    "get_schema_by_type",
    
    # 向量庫管理
    "load_paper_vectorstore",
    "load_experiment_vectorstore",
    "search_documents",
    "get_vectorstore_stats",
    "preview_chunks",
    "combine_search_results",
    "format_search_results",
    
    # 檢索功能
    "retrieve_chunks_multi_query",
    "retrieve_chunks_single_query",
    "expand_query",
    "expand_query_with_fallback",
    
    # LLM 生成
    "call_llm",
    "call_llm_structured_proposal",
    "call_llm_structured_experimental_detail",

    "call_llm_structured_revision_proposal",
    
    # 格式轉換
    "structured_proposal_to_text",
    "structured_experimental_detail_to_text",
    "structured_revision_proposal_to_text",
    
    # LLM 管理
    "LLMManager",
    "create_llm_manager",
    "get_default_llm_manager",
    
    # 模式管理
    "get_available_modes",
    "validate_mode",
    "get_mode_description",
    "get_mode_config",
    "get_modes_by_category",
    "is_structured_output_mode",
    "requires_experiment_data",
    "allows_inference",
    "get_mode_summary",
    
    # 處理器
    "BaseProcessor",
    "AdvancedInferenceProcessor",
    "ProposalProcessor",
    "InferenceProcessor",
    "StrictProcessor",
    "ExperimentDetailProcessor",
    "InnovationProcessor",
    "get_processor",
    
    # 提示詞構建
    "build_prompt",
    "build_inference_prompt",
    "build_proposal_prompt",
    "build_detail_experimental_plan_prompt",
    "build_dual_inference_prompt",
    "build_iterative_proposal_prompt"
]
