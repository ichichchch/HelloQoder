"""
RAGAS-based evaluation script for testing retrieval quality.
Success Criteria: Recall@5 > 0.8

Usage:
    python scripts/evaluate_recall.py --workspace /path/to/test/workspace
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import context_recall, context_precision

from app.config import get_settings
from app.vector_store import get_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_golden_dataset(dataset_path: str) -> list[dict[str, Any]]:
    """Load the golden evaluation dataset."""
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Evaluation dataset not found: {dataset_path}")
    
    with open(path) as f:
        data = json.load(f)
    
    return data.get("test_cases", [])


def create_evaluation_dataset(
    test_cases: list[dict[str, Any]],
    workspace_path: str,
) -> Dataset:
    """
    Create a RAGAS-compatible dataset from test cases.
    
    Each test case should have:
    - question: The query to search for
    - ground_truth: The expected relevant content/code
    - ground_truth_files: List of files that should be retrieved
    """
    store = get_vector_store()
    
    questions = []
    ground_truths = []
    contexts = []
    
    for case in test_cases:
        question = case.get("question", "")
        ground_truth = case.get("ground_truth", "")
        
        # Query the vector store
        results = store.query(
            query=question,
            workspace_path=workspace_path,
            top_k=5
        )
        
        # Extract retrieved contexts
        retrieved_contexts = [chunk.content for chunk in results]
        
        questions.append(question)
        ground_truths.append(ground_truth)
        contexts.append(retrieved_contexts)
    
    return Dataset.from_dict({
        "question": questions,
        "ground_truth": ground_truths,
        "contexts": contexts,
    })


def run_evaluation(
    dataset_path: str,
    workspace_path: str,
    threshold: float = 0.8
) -> dict[str, float]:
    """
    Run RAGAS evaluation on the retrieval system.
    
    Returns metrics including:
    - context_recall: Proportion of relevant info retrieved
    - context_precision: Proportion of retrieved info that is relevant
    """
    logger.info(f"Loading golden dataset from {dataset_path}")
    test_cases = load_golden_dataset(dataset_path)
    
    if not test_cases:
        logger.warning("No test cases found in dataset")
        return {"error": "No test cases found"}
    
    logger.info(f"Found {len(test_cases)} test cases")
    
    # First, ensure the workspace is indexed
    logger.info(f"Indexing workspace: {workspace_path}")
    store = get_vector_store()
    files_indexed, chunks_created = store.index_workspace(workspace_path)
    logger.info(f"Indexed {files_indexed} files, {chunks_created} chunks")
    
    # Create evaluation dataset
    logger.info("Creating evaluation dataset...")
    eval_dataset = create_evaluation_dataset(test_cases, workspace_path)
    
    # Run RAGAS evaluation
    logger.info("Running RAGAS evaluation...")
    results = evaluate(
        eval_dataset,
        metrics=[context_recall, context_precision],
    )
    
    # Extract metrics
    metrics = {
        "context_recall": float(results["context_recall"]),
        "context_precision": float(results["context_precision"]),
    }
    
    # Check against threshold
    recall = metrics["context_recall"]
    passed = recall >= threshold
    
    logger.info("=" * 50)
    logger.info("EVALUATION RESULTS")
    logger.info("=" * 50)
    logger.info(f"Context Recall@5: {recall:.4f}")
    logger.info(f"Context Precision: {metrics['context_precision']:.4f}")
    logger.info(f"Threshold: {threshold}")
    logger.info(f"Status: {'PASSED' if passed else 'FAILED'}")
    logger.info("=" * 50)
    
    if not passed:
        logger.error(
            f"Recall@5 ({recall:.4f}) is below threshold ({threshold}). "
            "Review chunking strategy and embedding model."
        )
    
    return {
        **metrics,
        "threshold": threshold,
        "passed": passed,
    }


def create_sample_dataset(output_path: str):
    """Create a sample golden dataset for testing."""
    sample_data = {
        "description": "Sample evaluation dataset for AL Agent RAG",
        "test_cases": [
            {
                "question": "How does the user authentication work?",
                "ground_truth": "User authentication is handled by checking credentials against the database and generating a JWT token.",
                "ground_truth_files": ["auth/login.py", "auth/jwt.py"]
            },
            {
                "question": "What is the database connection configuration?",
                "ground_truth": "Database connection uses SQLAlchemy with connection pooling configured in config.py.",
                "ground_truth_files": ["config.py", "database/connection.py"]
            },
            {
                "question": "How are API errors handled?",
                "ground_truth": "API errors are caught by exception handlers and returned as JSON responses with appropriate status codes.",
                "ground_truth_files": ["api/errors.py", "middleware/error_handler.py"]
            }
        ]
    }
    
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output, "w") as f:
        json.dump(sample_data, f, indent=2)
    
    logger.info(f"Sample dataset created at {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate RAG retrieval quality using RAGAS"
    )
    parser.add_argument(
        "--workspace",
        type=str,
        help="Path to the workspace to evaluate",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="Path to golden dataset (defaults to EVALUATION_DATASET env var)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="Minimum recall threshold (default: 0.8)",
    )
    parser.add_argument(
        "--create-sample",
        action="store_true",
        help="Create a sample golden dataset",
    )
    
    args = parser.parse_args()
    
    if args.create_sample:
        settings = get_settings()
        create_sample_dataset(settings.evaluation_dataset)
        return
    
    if not args.workspace:
        parser.error("--workspace is required for evaluation")
    
    settings = get_settings()
    dataset_path = args.dataset or settings.evaluation_dataset
    
    results = run_evaluation(
        dataset_path=dataset_path,
        workspace_path=args.workspace,
        threshold=args.threshold,
    )
    
    # Exit with error code if evaluation failed
    if not results.get("passed", False):
        sys.exit(1)


if __name__ == "__main__":
    main()
