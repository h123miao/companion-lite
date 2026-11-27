package com.companionlite.data

/**
 * 统一的请求结果包装：加载中 / 成功 / 失败三态。
 *
 * 为什么要有它？
 * - 界面不能只拿到"数据"，还要知道"现在是在转圈、还是失败了、失败原因是什么"。
 * - 网络错误必须翻译成人话（见 [RemoteCompanionRepository]），不能把
 *   `java.net.ConnectException` 直接甩给用户看。
 *
 * @param offlineFallback 失败时是否已经退回到演示数据。
 *        为 true 表示界面还有东西可展示，但必须显示「演示数据」标识；
 *        写入类操作（签到、回答）永远不允许降级，否则等于骗用户"提交成功了"。
 */
sealed interface UiState<out T> {

    data object Loading : UiState<Nothing>

    data class Success<T>(val data: T) : UiState<T>

    data class Error(
        val message: String,
        val offlineFallback: Boolean = false
    ) : UiState<Nothing>
}
