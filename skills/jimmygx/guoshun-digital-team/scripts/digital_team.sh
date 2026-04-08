#!/bin/bash
#=========================================
# 国顺数字团队协作脚本
# Digital Team Collaboration Script
#=========================================

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 默认配置
DEBATE_ROUNDS=3
DEBATE_TIMEOUT=60
MAX_PARALLEL=5

#=========================================
# 工具函数
#=========================================

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 输出分隔线
divider() { echo "========================================="; }

#=========================================
# 角色定义
#=========================================

ARCHITECT_PROMPT="你是一位资深系统架构师，拥有10年以上经验。你关注：
- 系统可扩展性和可维护性
- 技术债务和长期演进
- 性能优化和资源利用率
- 行业最佳实践和技术趋势

请以架构师的专业视角分析问题，给出全面而有深度的观点。"

DEVELOPER_PROMPT="你是一位全栈软件工程师，拥有5年以上开发经验。你关注：
- 代码可行性和实现难度
- 开发效率和代码质量
- 现有技术栈的适配性
- 调试和维护的便利性

请以程序员的务实视角分析问题，给出切实可行的建议。"

TESTER_PROMPT="你是一位资深测试工程师，拥有5年以上经验。你关注：
- 功能完整性和边界条件
- 回归风险和回归测试
- 自动化测试覆盖率和效率
- 用户体验和易用性

请以测试工程师的质量视角分析问题，找出潜在风险。"

PM_PROMPT="你是一位资深产品经理，拥有5年以上经验。你关注：
- 需求的合理性和优先级
- 业务价值和用户收益
- 实现成本和开发周期
- 竞争差异化和市场定位

请以产品经理的商业视角分析问题，给出以用户为中心的建议。"

#=========================================
# 辩论机制
#=========================================

run_debate() {
    local topic="$1"
    local rounds="${2:-$DEBATE_ROUNDS}"
    
    log_info "辩题：$topic"
    divider
    
    echo -e "${CYAN}=== 数字团队辩论赛 ===${NC}"
    echo -e "${CYAN}辩题：$topic${NC}"
    echo -e "${CYAN}轮次：$rounds 轮${NC}"
    divider
    
    # 正方观点（架构师）
    echo -e "${GREEN}【正方 - 架构师】${NC}"
    echo "$ARCHITECT_PROMPT"
    echo ""
    echo "立场：支持辩题，请给出有力的立论。"
    echo ""
    
    # 反方观点（程序员）
    echo -e "${YELLOW}【反方 - 程序员】${NC}"
    echo "$DEVELOPER_PROMPT"
    echo ""
    echo "立场：反对辩题，请给出有力的反驳。"
    echo ""
    
    # 交替辩论
    for ((i=1; i<=rounds; i++)); do
        echo -e "${CYAN}--- 第 $i 轮辩论 ---${NC}"
        echo -e "${GREEN}正方补充：${NC}"
        echo "(正方继续深化论点或回应反方观点)"
        echo ""
        echo -e "${YELLOW}反方补充：${NC}"
        echo "(反方继续深化论点或回应正方观点)"
        echo ""
    done
    
    # 主 Agent 总结
    echo -e "${CYAN}=== 主 Agent 裁判总结 ===${NC}"
    echo "综合正反双方观点："
    echo ""
    echo "【正方核心论点】"
    echo "- (从架构视角支持的核心优势)"
    echo ""
    echo "【反方核心论点】"
    echo "- (从实现视角反对的核心理由)"
    echo ""
    echo "【主 Agent 裁判】"
    echo "- 评估双方论点的充分性和合理性"
    echo "- 给出平衡的建议或明确的结论"
    divider
    log_success "辩论结束"
}

#=========================================
# 角色池
#=========================================

show_roles() {
    echo -e "${CYAN}=== 数字团队角色池 ===${NC}"
    divider
    echo -e "${GREEN}1. 架构师 (Architect)${NC}"
    echo "   特点：全局视角、技术深度"
    echo "   领域：系统设计、技术选型、性能优化"
    divider
    echo -e "${BLUE}2. 程序员 (Developer)${NC}"
    echo "   特点：务实实现、代码质量"
    echo "   领域：前端/后端开发、Bug修复"
    divider
    echo -e "${YELLOW}3. 测试工程师 (Tester)${NC}"
    echo "   特点：质量把关、风险识别"
    echo "   领域：自动化测试、回归测试"
    divider
    echo -e "${RED}4. 产品经理 (PM)${NC}"
    echo "   特点：用户视角、业务价值"
    echo "   领域：需求分析、优先级排序"
    divider
}

run_role_dispatch() {
    local task="$1"
    local roles="${2:-architect,developer,tester}"
    
    log_info "任务：$task"
    log_info "参与角色：$roles"
    divider
    
    echo -e "${CYAN}=== 数字团队角色协作 ===${NC}"
    echo -e "${CYAN}任务：$task${NC}"
    divider
    
    # 根据角色分发任务
    IFS=',' read -ra ROLE_ARRAY <<< "$roles"
    for role in "${ROLE_ARRAY[@]}"; do
        case "$role" in
            architect)
                echo -e "${GREEN}【架构师】${NC}"
                echo "$ARCHITECT_PROMPT"
                echo "任务：$task"
                echo "输出：架构设计方案和技术建议"
                divider
                ;;
            developer)
                echo -e "${BLUE}【程序员】${NC}"
                echo "$DEVELOPER_PROMPT"
                echo "任务：$task"
                echo "输出：实现方案和代码建议"
                divider
                ;;
            tester)
                echo -e "${YELLOW}【测试工程师】${NC}"
                echo "$TESTER_PROMPT"
                echo "任务：$task"
                echo "输出：测试策略和风险清单"
                divider
                ;;
            pm)
                echo -e "${RED}【产品经理】${NC}"
                echo "$PM_PROMPT"
                echo "任务：$task"
                echo "输出：产品方案和优先级建议"
                divider
                ;;
        esac
    done
    
    log_success "角色协作完成"
}

#=========================================
# 任务分发
#=========================================

run_task_assign() {
    local task="$1"
    
    log_info "任务：$task"
    divider
    
    echo -e "${CYAN}=== 数字团队任务分发 ===${NC}"
    echo -e "${CYAN}原始任务：$task${NC}"
    divider
    
    echo -e "${GREEN}【任务分析】${NC}"
    echo "主 Agent 分析任务，拆解成独立子任务..."
    echo ""
    
    echo -e "${GREEN}【任务拆解结果】${NC}"
    echo "子任务A：（无依赖，并行执行）"
    echo "  - 负责人：前端工程师"
    echo "  - 输出物：前端代码"
    echo ""
    echo "子任务B：（无依赖，并行执行）"
    echo "  - 负责人：后端工程师"
    echo "  - 输出物：API代码"
    echo ""
    echo "子任务C：（依赖A、B完成后执行）"
    echo "  - 负责人：测试工程师"
    echo "  - 输出物：测试报告"
    echo ""
    
    echo -e "${GREEN}【执行计划】${NC}"
    echo "阶段1（并行）：子任务A + 子任务B"
    echo "阶段2：子任务C"
    echo "阶段3：汇总验收"
    divider
    
    echo -e "${GREEN}【子任务执行】${NC}"
    echo "→ 子任务A 执行中..."
    echo "  完成：前端代码"
    echo ""
    echo "→ 子任务B 执行中..."
    echo "  完成：API代码"
    echo ""
    echo "→ 子任务C 执行中..."
    echo "  完成：测试报告"
    echo ""
    
    echo -e "${GREEN}【最终交付物】${NC}"
    echo "- 前端代码：xxx"
    echo "- 后端API：xxx"
    echo "- 测试报告：xxx"
    divider
    log_success "任务分发完成"
}

#=========================================
# 主入口
#=========================================

main() {
    local command="${1:-help}"
    local arg1="${2:-}"
    local arg2="${3:-}"
    
    case "$command" in
        debate)
            run_debate "$arg1" "$arg2"
            ;;
        roles)
            show_roles
            run_role_dispatch "$arg1" "$arg2"
            ;;
        assign)
            run_task_assign "$arg1"
            ;;
        help|--help|-h)
            echo "国顺数字团队协作技能"
            echo ""
            echo "用法："
            echo "  $0 debate <辩题> [轮次]     # 发起辩论"
            echo "  $0 roles <任务> [角色列表]  # 角色池协作"
            echo "  $0 assign <任务>             # 任务分发"
            echo "  $0 help                     # 显示帮助"
            echo ""
            echo "示例："
            echo "  $0 debate '要不要上微服务' 3"
            echo "  $0 roles '评审这个方案' 'architect,developer'"
            echo "  $0 assign '完成用户模块开发'"
            ;;
        *)
            log_error "未知命令：$command"
            echo "使用 $0 help 查看帮助"
            exit 1
            ;;
    esac
}

main "$@"
