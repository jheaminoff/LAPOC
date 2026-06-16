import styles from './PersonSelector.module.css'

type Props = {
  icon: string
  label: string
  description: string
  onClick: () => void
}

export default function PersonSelector({ icon, label, description, onClick }: Props) {
  return (
    <button className={styles.card} onClick={onClick} type="button">
      <span className={styles.icon}>{icon}</span>
      <h3 className={styles.label}>{label}</h3>
      <p className={styles.description}>{description}</p>
      <span className={styles.cta}>Get started →</span>
    </button>
  )
}
