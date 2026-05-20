#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time

def run_batch_proofread(novel_root, start_ep, end_ep):
    """
    지정된 회차 범위에 대해 runner.py를 순차적으로 호출하여 일괄 품질 검증 및 상태 추출을 진행합니다.
    이를 통해 LLM의 컨텍스트 분산을 차단하고 순차적인 상태 동기화 체인을 구축합니다.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    runner_path = os.path.join(script_dir, "runner.py")
    python_exe = sys.executable  # 현재 실행 중인 파이썬 인터프리터 경로 사용

    if not os.path.exists(runner_path):
        print(f"[Error] runner.py not found at: {runner_path}")
        return

    print("\n" + "="*60)
    print(f"[Batch Proofreader] Initializing Sequential Pipeline Run")
    print(f"   - Novel Root: {novel_root}")
    print(f"   - Target Range: Ep.{start_ep:03d} ~ Ep.{end_ep:03d}")
    print("="*60 + "\n")

    total_eps = end_ep - start_ep + 1
    success_count = 0
    start_time = time.time()

    for idx, ep in enumerate(range(start_ep, end_ep + 1), 1):
        ep_str = f"{ep:03d}"
        print(f"[{idx}/{total_eps}] Processing Episode {ep_str}...")
        
        # runner.py 호출 커맨드 조립
        cmd = [python_exe, runner_path, novel_root, ep_str]
        
        ep_start_time = time.time()
        try:
            # subprocess.run을 사용하여 출력을 스트리밍하고 에러 감지
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
            ep_duration = time.time() - ep_start_time
            print(f"    -> [Success] Ep.{ep_str} completed in {ep_duration:.2f}s.")
            success_count += 1
        except subprocess.CalledProcessError as e:
            ep_duration = time.time() - ep_start_time
            print(f"    [Error] Ep.{ep_str} failed after {ep_duration:.2f}s.")
            print(f"    [Details]: {e.stderr.strip()[:200]}...")
            # 강제 중단하지 않고 계속 진행할지 여부는 시나리오에 따르나, 일시적인 오류로 전체 배치가 끊기지 않도록 경고 후 진행합니다.
            continue

    total_duration = time.time() - start_time
    print("\n" + "="*60)
    print(f"[Batch Proofreader] Pipeline Run Completed")
    print(f"   - Total Processed: {total_eps} episodes")
    print(f"   - Successful: {success_count} / {total_eps}")
    print(f"   - Total Time: {total_duration:.2f} seconds")
    print("="*60 + "\n")

def main():
    if len(sys.argv) < 4:
        print("Usage: python batch_proofreader.py <novel_root_directory> <start_episode_num> <end_episode_num>")
        print("Example: python batch_proofreader.py j:\\eBooks\\MyNovel 1 10")
        sys.exit(1)

    novel_root = sys.argv[1]
    
    try:
        start_ep = int(sys.argv[2])
        end_ep = int(sys.argv[3])
    except ValueError:
        print("[Error] Episode numbers must be integers.")
        sys.exit(1)

    if start_ep > end_ep:
        print("[Error] Start episode must be less than or equal to end episode.")
        sys.exit(1)

    if not os.path.exists(novel_root):
        print(f"[Error] Novel root path does not exist: {novel_root}")
        sys.exit(1)

    run_batch_proofread(novel_root, start_ep, end_ep)

if __name__ == "__main__":
    main()
